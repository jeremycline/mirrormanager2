<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
<title>Public Active Mirrors</title>
</head>
<body>
<h2>By Version</h2>
<table border='1'>
<tr><th>Product</th><th>Version</th></tr>
<tr py:for="p in products">
<td><span py:replace="p.name">Product Name</span></td>
<td>
<span py:for="v in p.versions">
      <a href="${tg.url('/publiclist/' + str(p.id) + '/' + str(p.id))}"><span py:replace="v.name">Version</span></a>
</span>
</td>
</tr>
</table>
<h2>Public Active Mirrors</h2>
<table border='1'>
<tr><th>Country</th><th>Site</th><th>Host</th><th>Content</th><th>Bandwidth</th><th>Comments</th></tr>
<tr py:for="host in hosts">
<td><span py:replace="host.country">Country</span></td>
<td><a href="${host.site.orgUrl}"><span py:replace="host.site.name">Site Name</span></a></td>
<td><span py:replace="host.name">Host Name</span></td>
<td>
<table>
<tr py:for="hc in host.categories" py:if="len(hc.dirs) > 0">
<td><span py:replace="hc.category.name">Category name</span></td>
<?python
http=None
ftp=None
rsync=None
for u in hc.urls:
    if not u.private:
        if u.url.startswith('http:'):
	    http=u.url
        elif u.url.startswith('ftp:'):
	    ftp=u.url
        elif u.url.startswith('rsync:'):
	    rsync=u.url
?>
<td><span py:if="http is not None"><a href="${http}">http</a></span></td>
<td><span py:if="ftp is not None"><a href="${ftp}">ftp</a></span></td>
<td><span py:if="rsync is not None"><a href="${rsync}">rsync</a></span></td>
</tr>
</table>
</td>
<td><span py:replace="host.bandwidth">Bandwidth</span></td>
<td><span py:replace="host.comment">Comment</span></td>
</tr>
</table>



</body>
</html>