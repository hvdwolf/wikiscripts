import sys, urllib2

if len(sys.argv) > 1:
	wikilang = str(sys.argv[1])
	baseurl = 'http://dumps.wikimedia.org/' + wikilang + 'wiki/latest/'
	filename = wikilang + 'wiki-latest-externallinks.sql.gz'
	#print "Downloading: " + baseurl+filename
	# Retrieve url and save as filename
	u = urllib2.urlopen(baseurl+filename)
	f = open(filename, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	#print "Downloading: %s Bytes: %s KB" % (filename, file_size/1024)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d KB [%3.2f%%]" % (file_size_dl/1024, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,

	f.close()
