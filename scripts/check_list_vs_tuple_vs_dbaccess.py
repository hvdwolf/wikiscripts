#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.1, 2015-05-03, Harry van der Wolf
# According to all python rules lists should be much slower then tuples, so I created this check script
# And of course compare with database access.
import os, sys, time, sqlite3

reload(sys)  
sys.setdefaultencoding('utf8')

# Try with the largest database being the english one
SQLITE_DATABASE = '/cygdrive/d/LocalData_387640/Datadir/Navigatie/wikiscripts/sqlite/enwikipedia.db'  # This needs to be a full qualified path
wikidb = sqlite3.connect(SQLITE_DATABASE)
cursor = wikidb.cursor()

start = time.time()
cursor.execute('select * from en_externallinks')
linkrows = cursor.fetchall()
print('sql retrieval time: ' + str(time.time() -start))
print('Number of rows retrieved from en_externallinks: '+str(len(linkrows))+'\n')

print('loop through list')
extlinkdata = [None] * 6
start = time.time()
for row in linkrows:
	extlinkdata[0] = row[0]
	extlinkdata[1] = row[1]		# latitude
	extlinkdata[2] = row[2]		# longitude
	extlinkdata[3] = row[3]		# language
	extlinkdata[4] = row[4]		# poitype
	extlinkdata[5] = row[5]		# region
print('linkrows: ' + str(time.time() -start))

print('\nconvert to tuple')
start = time.time()
tuplerows = tuple(linkrows)
print('conversion time: ' + str(time.time() -start))

print('\nloop through tuple')
start = time.time()
for row in tuplerows:
	extlinkdata[0] = row[0]
	extlinkdata[1] = row[1]		# latitude
	extlinkdata[2] = row[2]		# longitude
	extlinkdata[3] = row[3]		# language
	extlinkdata[4] = row[4]		# poitype
	extlinkdata[5] = row[5]		# region
print('tuplerows: ' + str(time.time() -start))

print('\nNow test on where title="Zwolle" in listrows')
for row in linkrows:
	if row[0] == "Zwolle":
		extlinkdata[0] = row[0]
		extlinkdata[1] = row[1]		# latitude
		extlinkdata[2] = row[2]		# longitude
		extlinkdata[3] = row[3]		# language
		extlinkdata[4] = row[4]		# poitype
		extlinkdata[5] = row[5]		# region
print('linkrows Zwolle: ' + str(time.time() -start))

print('\nNow test on where title="Zwolle" in tuplerows')
for row in tuplerows:
	if row[0] == "Zwolle":
		extlinkdata[0] = row[0]
		extlinkdata[1] = row[1]		# latitude
		extlinkdata[2] = row[2]		# longitude
		extlinkdata[3] = row[3]		# language
		extlinkdata[4] = row[4]		# poitype
		extlinkdata[5] = row[5]		# region
print('tuplerows Zwolle: ' + str(time.time() -start))


print('\nNow via database access test on where title="Zwolle" in en_externallinks')
start = time.time()
# do a stupid fetchall instead of fetchone
cursor.execute('select * from en_externallinks where title="Zwolle"')
linkrows = cursor.fetchall()
for row in linkrows:
	extlinkdata[0] = row[0]
	extlinkdata[1] = row[1]		# latitude
	extlinkdata[2] = row[2]		# longitude
	extlinkdata[3] = row[3]		# language
	extlinkdata[4] = row[4]		# poitype
	extlinkdata[5] = row[5]		# region
print('db access: ' + str(time.time() -start))

