%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from
%distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           mirrormanager2
Version:        0.7.3
Release:        1%{?dist}
Summary:        Mirror management application

# Most MirrorManager files are licensed under the MIT license. Some
# imported/derivated parts like zebra-dump-parser or the the script
# to generate the worldmaps are licensed under GPLv2 and GPLv2+
License:        MIT and GPLv2+ and GPLv2
URL:            http://fedorahosted.org/mirrormanager/
Source0:        https://fedorahosted.org/releases/m/i/mirrormanager/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-flask
BuildRequires:  python-flask-admin
BuildRequires:  python-flask-xml-rpc
BuildRequires:  python-flask-wtf
BuildRequires:  python-wtforms
BuildRequires:  python-IPy < 0.80
BuildRequires:  python-dns
BuildRequires:  python-fedora >= 0.3.33
BuildRequires:  python-fedora-flask >= 0.3.33
BuildRequires:  python-setuptools
BuildRequires:  python-psutil
BuildRequires:  python-alembic
# Mirrorlist
BuildRequires:  python-GeoIP
BuildRequires:  py-radix
BuildRequires:  python-webob

BuildRequires:  systemd-devel

# EPEL6
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
BuildRequires:  python-sqlalchemy0.7
%else
BuildRequires:  python-sqlalchemy >= 0.7
%endif

Requires:  python-flask
Requires:  python-flask-admin
Requires:  python-flask-xml-rpc
Requires:  python-flask-wtf
Requires:  python-wtforms
Requires:  python-fedora >= 0.3.33
Requires:  python-fedora-flask >= 0.3.33
Requires:  python-setuptools
Requires:  python-psutil
Requires:  python-alembic

Requires:  %{name}-lib == %{version}
Requires:  mod_wsgi

%description
MirrorManager keeps track of the public and private mirrors, that carry
Fedora, EPEL, and RHEL content. It is used by the Fedora infrastructure as
well as rpmfusion.org, a third-party repository.
It automatically selects the “best” mirror for a given user based on a set
of fallback heuristics (such as network, country or continent).


%package lib
Summary:        Library to interact with MirrorManager's database
Group:          Development/Tools
BuildArch:      noarch

Requires:  python-IPy < 0.80
Requires:  python-dns

# EPEL6
%if ( 0%{?rhel} && 0%{?rhel} == 6 )
Requires:  python-sqlalchemy0.7
%else
Requires:  python-sqlalchemy >= 0.7
%endif

%description lib
Library to interact with MirrorManager's database


%package mirrorlist
Summary:        MirrorList serving mirrors to yum/dnf
Group:          Development/Tools
BuildArch:      noarch

Requires:  python-GeoIP
Requires:  py-radix
Requires:  python-webob
Requires:  python-IPy
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description mirrorlist
Sub-part of mirrormanager serving mirrors to yum/dnf


%package crawler
Summary:        Crawler for MirrorManager
Group:          Development/Tools
BuildArch:      noarch

Requires:  %{name}-lib == %{version}
Requires:  python-GeoIP
Requires(pre):  shadow-utils

%description crawler
Install the crawler for MirrorManager, crawling all the mirrors to find out
if they are up to date or not


%package backend
Summary:        Backend scripts for MirrorManager
Group:          Development/Tools
BuildArch:      noarch

Requires:  %{name}-lib == %{version}
Requires(pre):  shadow-utils

%description backend
Install a number of utility scripts to be used manually or in cron jobs to
run MirrorManager.

%package client
Summary:        Fedora mirror management system downstream mirror tools
Group:          Applications/Internet
BuildArch:      noarch

%description client
Client-side, run on each downstream mirror, to report back to the
MirrorManager database a description of the content carried by that
mirror.

%package statistics
Summary:        Scripts to generate MirrorManager statistics
Group:          Applications/Internet
BuildArch:      noarch

Requires:  %{name}-lib == %{version}
Requires:  python-GeoIP
Requires:  python-matplotlib
Requires:  python-basemap

%description statistics
A collection of different statistics script which are analyzing
MirrorManager content or log files. It contains scripts to analyze
the mirrorlist server connections, draws maps of all available mirrors
and can also visualize how fast the master data propagates to all the
mirrors. As it depends on matplotlib it has a rather large dependency
tree.

%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

# Create directories needed
# Apache configuration files
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/
# MirrorManager configuration file
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/mirrormanager
# MirrorManager crawler log rotation
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d
# for .wsgi files mainly
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2
# Stores temp files (.sock & co)
mkdir -p $RPM_BUILD_ROOT/%{_sharedstatedir}/mirrormanager
# Results and homedir
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lib/mirrormanager
# Lock files
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/lock/mirrormanager
# Stores lock and pid info
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/run/mirrormanager
# Log files
mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/log/mirrormanager/crawler
# Stores the service file for systemd
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}

# Install apache configuration file
install -m 644 mirrorlist/apache/mirrorlist-server.conf \
    $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/mirrorlist-server.conf
install -m 644 utility/mirrormanager.conf.sample \
    $RPM_BUILD_ROOT/%{_sysconfdir}/httpd/conf.d/mirrormanager.conf

# Install configuration file
install -m 644 utility/mirrormanager2.cfg.sample \
    $RPM_BUILD_ROOT/%{_sysconfdir}/mirrormanager/mirrormanager2.cfg

# Install crawler logrotate definition
install -m 644 utility/mm2_crawler.logrotate \
    $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/mm2_crawler

# Install umdl logrotate definition
install -m 644 utility/mm2_umdl.logrotate \
    $RPM_BUILD_ROOT/%{_sysconfdir}/logrotate.d/mm2_umdl

# Install WSGI file
install -m 644 utility/mirrormanager2.wsgi \
    $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/mirrormanager2.wsgi
install -m 644 mirrorlist/mirrorlist_client.wsgi \
    $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/mirrorlist_client.wsgi

# Install the mirrorlist server
install -m 644 mirrorlist/mirrorlist_server.py \
    $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/mirrorlist_server.py
install -m 644 mirrorlist/weighted_shuffle.py \
    $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/weighted_shuffle.py

# Install the createdb script
install -m 644 createdb.py \
    $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/mirrormanager2_createdb.py

# Install the tmpfile creating the /run/mirrormanager folder upon reboot
mkdir -p %{buildroot}%{_tmpfilesdir}
install -m 0644 mirrorlist/systemd/mirrormanager_tempfile.conf \
    $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{name}-mirrorlist.conf
install -m 0644 utility/backend_tempfile.conf \
    $RPM_BUILD_ROOT/%{_tmpfilesdir}/%{name}-backend.conf

# Install the systemd service file
install -m 644 mirrorlist/systemd/mirrorlist-server.service \
    $RPM_BUILD_ROOT/%{_unitdir}/mirrorlist-server.service

# Install the alembic files
cp -r alembic $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/
install -m 644 utility/alembic.ini $RPM_BUILD_ROOT/%{_sysconfdir}/mirrormanager/alembic.ini

# Install the zebra-dump-parser perl module
cp -r utility/zebra-dump-parser $RPM_BUILD_ROOT/%{_datadir}/mirrormanager2/

# Install the client files
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/mirrormanager-client
install -m 0644 client/report_mirror.conf \
    $RPM_BUILD_ROOT/%{_sysconfdir}/mirrormanager-client/report_mirror.conf


%pre mirrorlist
getent group mirrormanager >/dev/null || groupadd -r mirrormanager
getent passwd mirrormanager >/dev/null || \
    useradd -r -g mirrormanager -d %{_localstatedir}/lib/mirrormanager -s /sbin/nologin \
    -c "MirrorManager" mirrormanager
exit 0

%pre crawler
getent group mirrormanager >/dev/null || groupadd -r mirrormanager
getent passwd mirrormanager >/dev/null || \
    useradd -r -g mirrormanager -d %{_localstatedir}/lib/mirrormanager -s /sbin/nologin \
    -c "MirrorManager" mirrormanager
exit 0

%pre backend
getent group mirrormanager >/dev/null || groupadd -r mirrormanager
getent passwd mirrormanager >/dev/null || \
    useradd -r -g mirrormanager -d %{_localstatedir}/lib/mirrormanager -s /sbin/nologin \
    -c "MirrorManager" mirrormanager
exit 0

%post mirrorlist
%systemd_post mirrorlist-server.service

%preun mirrorlist
%systemd_preun mirrorlist-server.service

%postun mirrorlist
%systemd_postun_with_restart mirrorlist-server.service

%check
# One day we will have unit-tests to run here

%files
%doc README.rst LICENSE-MIT-X11 LICENSE-GPLv2 doc/
%config(noreplace) %{_sysconfdir}/httpd/conf.d/mirrormanager.conf
%config(noreplace) %{_sysconfdir}/mirrormanager/mirrormanager2.cfg

%dir %{_sysconfdir}/mirrormanager/
%dir %{python_sitelib}/%{name}/

%{_sysconfdir}/mirrormanager/alembic.ini

%{_datadir}/mirrormanager2/mirrormanager2.wsgi
%{_datadir}/mirrormanager2/mirrormanager2_createdb.py*
%{_datadir}/mirrormanager2/alembic/

%{python_sitelib}/%{name}/*.py*
%{python_sitelib}/%{name}/templates/
%{python_sitelib}/%{name}/static/
%{python_sitelib}/%{name}*.egg-info


%files lib
%{python_sitelib}/%{name}/lib/
%{python_sitelib}/%{name}/__init__.py*


%files mirrorlist
%config(noreplace) %{_sysconfdir}/httpd/conf.d/mirrorlist-server.conf
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/run/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/lib/mirrormanager/
%{_tmpfilesdir}/%{name}-mirrorlist.conf
%{_unitdir}/mirrorlist-server.service
%{_datadir}/mirrormanager2/mirrorlist_client.wsgi
%{_datadir}/mirrormanager2/mirrorlist_server.py*
%{_datadir}/mirrormanager2/weighted_shuffle.py*


%files crawler
%config(noreplace) %{_sysconfdir}/logrotate.d/mm2_crawler
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/lib/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/log/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/log/mirrormanager/crawler
%{_bindir}/mm2_crawler


%files backend
%config(noreplace) %{_sysconfdir}/logrotate.d/mm2_umdl
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/lock/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/lib/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/log/mirrormanager
%attr(755,mirrormanager,mirrormanager) %dir %{_localstatedir}/run/mirrormanager
%{_tmpfilesdir}/%{name}-backend.conf
%{_datadir}/mirrormanager2/zebra-dump-parser/
%{_bindir}/mm2_emergency-expire-repo
%{_bindir}/mm2_get_global_netblocks
%{_bindir}/mm2_get_internet2_netblocks
%{_bindir}/mm2_move-devel-to-release
%{_bindir}/mm2_move-to-archive
%{_bindir}/mm2_refresh_mirrorlist_cache
%{_bindir}/mm2_update-EC2-netblocks
%{_bindir}/mm2_update-master-directory-list
%{_bindir}/mm2_umdl2
%{_bindir}/mm2_update-mirrorlist-server
%{_bindir}/mm2_create_install_repo
%{_bindir}/mm2_upgrade-install-repo


%files client
%dir %{_sysconfdir}/mirrormanager-client
%config(noreplace) %{_sysconfdir}/mirrormanager-client/report_mirror.conf
%{_bindir}/report_mirror

%files statistics
%{_bindir}/mm2_generate-worldmap
%{_bindir}/mm2_propagation
%{_bindir}/mirrorlist_statistics

%changelog
* Thu Jun 23 2016 Adrian Reber <adrian@lisas.de> - 0.7.3-1
- Update to 0.7.3
- Allow submission of checkin information via json (Patrick Uiterwijk)
  https://github.com/fedora-infra/mirrormanager2/issues/170
- Add logging to checkin code (Patrick Uiterwijk)
- mm2_crawler: Add missing field to stats dict
  https://github.com/fedora-infra/mirrormanager2/issues/176
- mirrolist: fix &redirect=1
  https://github.com/fedora-infra/mirrormanager2/issues/178

* Wed Jun 15 2016 Adrian Reber <adrian@lisas.de> - 0.7.2-1
- Update to 0.7.2
- Fix propagation diagram creation
- Use yesterday's date in get_global_netblocks
- Mark path containing /stage/ as testing
- Added an option with which the user can define the preferred
  protocol)
- Adjust repomap for the new repo layout (Pierre-Yves Chibon)
- Typo fix in readme (Taranjeet)

* Mon Feb 01 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.7.1-1
- Update to 0.7.1
- Fixes to the emergency script (Adrian Reber and Patrick Uiterwijk)

* Wed Jan 13 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.7-1
- Update to 0.7
- Fix various matplotlib problems in the statitics (Adrian Reber)
- Make green be synced and red be older in the propagation page (Patrick
  Uiterwijk)
- Add the possibility to clear all old files from a repo (to ensure users have
  only up to date mirrors) (Patrick Uiterwijk)
- Do not load the host config until it's asked (Drops the memory usage and
  increase the speed of the application) (Adrian Reber)

* Thu Dec 17 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6.1-1
- Update to 0.6.1
- Fix mirrorlist to access info from the just loaded pickle (Patrick Uiterwijk)

* Wed Dec 16 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.6-1
- Update to 0.6
- Really ensure that new host is admin_active (Seth Jennings)
- Add the possibility to kill rsync after some time
- Add headers to the table listing the mirrors
- Cascade deletion and bring back the rsyncFilter endpoint
- Fix to the crawler (Adrian Reber)
- Improved documentation and validation
- Optionally exclude certain protocols from MM (Adrian Reber)
- Import generate-worldmap from MM1 (Adrian Reber)
- Optionally display mirrorlist statistics (Adrian Reber)
- mirrorlist: Remove --debug option (Adrian Reber)
- More mirrorlist statistics changes and spec file integration (Adrian Reber)
- Switch the MirrorList server to use threading rather than forking (Patrick
  Uiterwijk)

* Mon Sep 07 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.5.1-1
- Update to 0.5.1
- Deleting URLs if site or host is removed (avoids the situation where a host is
  removed and then someone tries to re-add it) (Adrian Reber)
- Ensure that new host and new site are admin_active

* Fri Sep 04 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.5-1
- Update to 0.5
- Add order option to get_file_detail() (Adrian Reber)
- Remove all whitespaces around the mirror URLs (Adrian Reber)
- Sort metalinks alternates by timestamps descending (Adrian Reber)
- Rewrite the UMDL2 into a UMDL2
- Add code to graph repomd.xml propagation (Adrian Reber)
- Rotate crawler logs once per week (Adrian Reber)
- Update the UMDL1 to share code with the UMDL2 (Adrian Reber)
- Remove trailing slash of site and host_category_url

* Thu Jul 30 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.2-1
- Update to 0.4.2
- Create the -client subpackage containing the report_mirror script and
  configuration file (Adrian Reber)

* Tue Jul 28 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.1-1
- Update to 0.4.1
- If the host has no categories do not auto-disable it (Adrian Reber)
- Different small umdl and crawler fixe (Adrian Reber)

* Wed Jul 22 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.4.0-1
- Update to 0.4.0
- Add utility script to update the MM2 DB for a single file (light-weight UMDL
  for a single file) (Ralph Bean)
- Add support to gracefully shutdown the crawler (Adrian Reber)
- Add support to limit crawling by continent (Adrian Reber)
- Fix the crawler to work properly with MM2
- Fix the repomap to create properly development repos
- Fix new repository detection and creation in UMDL (Adrian Reber)

* Thu Jul 02 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.3.1-1
- Update to 0.3.1
- Fix for broken logging output in the UMDL (Adrian Reber)
- Fix mm2_move-to-archive (Adrian Reber)

* Wed Jun 24 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.3.0-1
- Update to 0.3.0
- Fix the --delete action of the umdl (Adrian Reber)
- If the user is not an admin, keep the existing admin_active settings
- Only MM2 admins are allowed to change the always_up2date flag of a mirror
- Also fix the mm2_crawler logrotate script like the one for umdl (Adrian Reber)

* Thu Jun 11 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.2.1-1
- Update to 0.2.1
- Fix the mm2_move-devel-to-release script to work properly with MM2 and our
  products (Adrian Reber)

* Fri Jun 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.2.0-1
- Update to 0.2.0
- Include the background header file in MM2 itself (Adrian Reber)
- Support always update hosts which are unreachable in the crawler (Adrian
  Reber)
- Adjust the spec file to the systemd packaging guidelines for Fedora
- Multiple improvements to the crawler, including a start of a canary mode
  (Adrian Reber)
- Offer possibility to sort by product, bringing back MM1 behavior (Adrian
  Reber)
- Couple of UI fixes about who is allowed to access what
- Fix peer ASNs (in the same spirit, who can access)
- Create noauthed master for mirror publiclist so that it can be cached in
  memcachd (Patrick Uiterwijk)
- Fix the report_mirror to correctly catch the xmlrpclib.ProtocolError
- Add a new utility script to upgrade repo from -alpha or -beta to release
- Adjust the logrotate configuration to fix the permission denied error
- Create 2 API endpoints, one for zodbot's .mirroradmin and one for nagios

* Thu May 07 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1.0-1
- Update 0.1.0
- Add the possibilities to delete a site or a host
- Do not only create /var/lock/mirrormanager on installation (Adrian Reber)

* Tue May 05 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.10-1
- Update to 0.0.10
- Install the mm2_create_install_repo script
- Fix version handling on mm2_create_install_repo (Adrian Reber)
- Fix pickle generation when several repositories point to the same directory

* Mon May 04 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.9-1
- Update to 0.0.9
- Include and install alembic files
- Try explicit garbage collection in the crawler (Adrian Reber)
- Use defined timeout also for HTTP/FTP connections (Adrian Reber)
- Add documentation about the crawler (Adrian Reber)
- Also add a /var/run directory for the backend (Adrian Reber)
- Add fedmenu integration
- Add new utility script to be used to create the fedora-install-X repositories
- Added last-sync script as mm2_last-sync (Adrian Reber)

* Thu Apr 23 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.8-1
- Update to 0.0.8
- Make MM2 a little prettier on high-res display
- Add a Location tag for static (Patrick Uiterwijk)
- Fix the DB session issue on the crawler (Adrian Reber)
- Add some documentation on how MirrorManager works
- Decrease time required for set_not_up2date() (Adrien Reber)
- Add support to auto disable mirrors (Adrien Reber)
- Auto disable hosts which have a URL configured but which does not exist
  (Adrian Reber)
- crawl_duration is a host specific property (Adrian Reber)
- Handle lighttpd returing a content length for directories (Adrian Reber)
- Scan the directories which are supposed to be on each mirror (Adrian Reber)
- Use Yesterday's date on mm2_get_internet2_netblocks to avoid TZ issue (Adrian
  Reber)
- Fix logging in the UMDL script (Adrian Reber)
- Allow the UMDL to crawl only a specified category (Adrian Reber)
- Fix example fedmsg config (Ralph Bean)

* Mon Apr 13 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.7-1
- Update to 0.0.7
- Add missing import on mm2_update-EC2-netblocks
- Have the cron jobs running under a ``mirrormanager`` user (Adrian Reber)
- Update the last_crawled and last_crawled_duration correctly (Adrian Reber)
- Fix systemd's tempfile.conf for mirrormanager2
- Fix link to the crawler log file (Adrian Reber)
- Close per thread logging correctly (Adrian Reber)
- Add more informations to the log output (Adrian Reber)
- Start crawling the hosts which require the most time (Adrian Reber)
- Filters the hosts to crawl at the DB level to save time and memory (Adrian
  Reber)
- Fix the xmlrpc endpoint (Adrian Reber)
- Adjust Build Requires to include systemd-devel instead of just systemd
- Close session at the end and make the session permanent
- Add new columns to the host table to store extra infos (Adrian Reber)
- Use urllib2 instead of urlgrabber in the crawler (Adrian Reber)
- Fix crawler timeout (Adrian Reber)
- run_rsync() returns a temporary file which needs to be closed (Adrian Reber)

* Wed Mar 18 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.6-1
- Update to 0.0.6
- Drop the Locations in the hosts (no longer used)
- Add unit-tests
  - To the frontend
  - To some of the backend scripts
- Add dependency to python-IPy
- Fix ExecStart instruction for systemd
- Fix apache configuration file for mirrorlist
- Fix host selection logic in the crawler (Adrian Reber)
- Log the rsync command (Adrian Reber)
- Add the possibility to specify the rsync argument via the configuration file
  (Adrian Reber)
- Add and install a tempfile.d file for systemd to re-create
  /var/run/mirrormanager upon reboot

* Mon Dec 15 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.5-1
- Update to 0.0.5
- Include zebra-dump-parser in the backend sub-package
- Install weighted_shuffle and include it in the mirrorlist sub-package

* Mon Dec 15 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.4-1
- Update to 0.0.4
- Fix  typos in the script to point them to the correct configuration file by
  default
- Install the mirrorlist_server
- Move mirrorlist to rely on systemd instead of supervisor
- Install zebra-dump-parser user by mm2_get_internet2_netblocks
- Remove debugging statement for mm2_refresh_mirrorlist_cache, no need to output
  something if everything ran fine

* Mon Dec 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.3-1
- Update to 0.0.3
- Fix the import in the createdb script

* Mon Dec 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.2-1
- Update to 0.0.2
- Move the flask application to mirrormanager2/app.py and put a module
  place holder in mirrormanager2/__init__.py that we can extract when
  splitting the module in -lib

* Mon Dec 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.1-2
- Fix the package name in the Requires, using %%{name} fixes things

* Mon Dec 08 2014 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.0.1-1
- Initial packaging work for Fedora
