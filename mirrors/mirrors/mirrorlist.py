import cherrypy
import turbogears
from turbogears import controllers, expose, validate, redirect, widgets, validators, error_handler, exception_handler
from sqlobject import *
from sqlobject.sqlbuilder import *
from mirrors.model import *
from IPy import IP

# key is directoryname
mirrorlist_cache = {}

# key is strings in tuple (repo.prefix, arch)
repo_arch_to_directoryname = {}

# key is an IPy.IP structure, value is list of host ids
host_netblock_cache = {}

# key is hostid, value is list of countries to allow
host_country_allowed_cache = {}

def _do_query_directories():
    sql =  'SELECT * FROM '
    sql += '(SELECT directory.name AS dname, host.id, host.country, host_category_url.url, site.private, host.private, host.internet2, host.internet2_clients '
    sql += 'FROM directory, host_category_dir, host_category, host_category_url, host, site, category_directory '
    sql += 'WHERE host_category_dir.host_category_id = host_category.id ' # join criteria
    sql += 'AND   host_category_url.host_category_id = host_category.id ' # join criteria
    sql += 'AND   host_category.host_id = host.id '                       # join criteria
    sql += 'AND   host.site_id = site.id '                                # join criteria
    sql += 'AND   host_category_dir.directory_id = directory.id '         # join criteria
    sql += 'AND   category_directory.directory_id = directory.id '         # join criteria (dir for this category)
    sql += 'AND   category_directory.category_id = host_category.category_id ' # join criteria
    sql += 'AND   host_category_dir.up2date '
    sql += 'AND NOT host_category_url.private '
    sql += 'AND host.user_active AND site.user_active '
    sql += 'AND host.admin_active AND site.admin_active '
    # now add the always_up2date host_categories
    sql += 'UNION '
    sql += 'SELECT directory.name AS dname, host.id, host.country, host_category_url.url, site.private, host.private, host.internet2, host.internet2_clients '
    sql += 'FROM directory, host_category, host_category_url, host, site, category_directory '
    sql += 'WHERE host_category_url.host_category_id = host_category.id ' # join criteria
    sql += 'AND   host_category.host_id = host.id '                       # join criteria
    sql += 'AND   host.site_id = site.id '                                # join criteria
    sql += 'AND   category_directory.directory_id = directory.id '         # join criteria (dir for this category)
    sql += 'AND   category_directory.category_id = host_category.category_id ' # join criteria
    sql += 'AND   host_category.always_up2date '
    sql += 'AND NOT host_category_url.private '
    sql += 'AND host.user_active AND site.user_active '
    sql += 'AND host.admin_active AND site.admin_active) '
    sql += 'AS subquery '
    sql += 'ORDER BY dname '

    directory = Directory.select()[0]
    result = directory._connection.queryAll(sql)
    return result

def populate_directory_cache():
    global repo_arch_to_directoryname
    result = _do_query_directories()

    cache = {}
    for (directoryname, hostid, country, hcurl, siteprivate, hostprivate, i2, i2_clients) in result:
        if directoryname not in cache:
            cache[directoryname] = {'global':[], 'byCountry':{}, 'byHostId':{}, 'ordered_mirrorlist':False, 'byCountryInternet2':{}}
            directory = Directory.byName(directoryname)
            repo = directory.repository
            # if a directory is in more than one category, problem...
            if repo is not None:
                repo_arch_to_directoryname[(repo.prefix, repo.arch.name)] = directory.name
                category = repo.category
                cache[directoryname]['ordered_mirrorlist'] = repo.version.ordered_mirrorlist
            else:
                numcats = len(directory.categories)
                if numcats == 0:
                    # no category, so we can't know a mirror host's URLs.
                    # nothing to add.
                    continue
                elif numcats >= 1:
                    # any of them will do, so just look at the first one
                    category = directory.categories[0]
                
            cache[directoryname]['subpath'] = directoryname[len(category.topdir.name)+1:]
            del repo
            del directory
            del category
            
        if country is not None:
            country = country.upper()
        v = (hostid, hcurl)
        if not siteprivate and not hostprivate:
            cache[directoryname]['global'].append(v)

            if country is not None:
                if not cache[directoryname]['byCountry'].has_key(country):
                    cache[directoryname]['byCountry'][country] = [v]
                else:
                    cache[directoryname]['byCountry'][country].append(v)

        if country is not None and i2 and ((not siteprivate and not hostprivate) or i2_clients):
            if not cache[directoryname]['byCountryInternet2'].has_key(country):
                cache[directoryname]['byCountryInternet2'][country] = [v]
            else:
                cache[directoryname]['byCountryInternet2'][country].append(v)

        if not cache[directoryname]['byHostId'].has_key(hostid):
            cache[directoryname]['byHostId'][hostid] = [v]
        else:
            cache[directoryname]['byHostId'][hostid].append(v)

    global mirrorlist_cache
    mirrorlist_cache = cache

def populate_netblock_cache():
    cache = {}
    for host in Host.select():
        if host.is_active() and len(host.netblocks) > 0:
            for n in host.netblocks:
                try:
                    ip = IP(n.netblock)
                except:
                    continue
                if cache.has_key(ip):
                    cache[ip].append(host.id)
                else:
                    cache[ip] = [host.id]

    global host_netblock_cache
    host_netblock_cache = cache

def populate_host_country_allowed_cache():
    cache = {}
    for host in Host.select():
        if host.is_active() and len(host.countries_allowed) > 0:
            cache[host.id] = [c.country.upper() for c in host.countries_allowed]
    global host_country_allowed_cache
    host_country_allowed_cache = cache

def host_bandwidth_cache():
    cache = {}
    for host in Host.select():
        cache[host.id] = host.bandwidth_int
    return cache

def host_country_cache():
    cache = {}
    for host in Host.select():
        cache[host.id] = host.country
    return cache

def repository_redirect_cache():
    cache = {}
    for r in RepositoryRedirect.select():
        cache[r.fromRepo] = r.toRepo
    return cache

def country_continent_redirect_cache():
    cache = {}
    for c in CountryContinentRedirect.select():
        cache[c.country] = c.continent
    return cache

def disabled_repository_cache():
    cache = {}
    for r in Repository.select():
        if r.disabled:
            cache[r.prefix] = True
    return cache

def populate_all_caches():
    populate_host_country_allowed_cache()
    populate_netblock_cache()
    populate_directory_cache()
    print "mirrorlist caches populated"



import cPickle as pickle
def dump_caches():
    data = {'mirrorlist_cache':mirrorlist_cache,
            'host_netblock_cache':host_netblock_cache,
            'host_country_allowed_cache':host_country_allowed_cache,
            'repo_arch_to_directoryname':repo_arch_to_directoryname,
            'repo_redirect_cache':repository_redirect_cache(),
            'country_continent_redirect_cache':country_continent_redirect_cache(),
            'disabled_repositories':disabled_repository_cache(),
            'host_bandwidth_cache':host_bandwidth_cache()}
            'host_country_cache':host_country_cache()}
    
    try:
        f = open('/tmp/mirrorlist_cache.pkl', 'w')
        pickle.dump(data, f)
        f.close()
    except:
        pass
