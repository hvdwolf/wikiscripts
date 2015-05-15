#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.3, 2015-05-15, Harry van der Wolf
# This file must be used on a compressed xml.bz file
# Usage: python parse_wikidump.py <iso-639-1 language code>
# example: python parse_wikidump.py en
# Note: wikipedia works per language!, not per country. 
# See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes for those codes.
# As an example "python parse_wikidump.py de" will convert the German language version, which is of course for every German speaker/reader.
# This script will always write a GPX file and can optionally write a CSV and/or OSM file.

# Note: do not attempt some "buffered" writes to memory and then once every xyz lines to file.
# That is much slower than simple write line by line
#
# Note 2 (windows): cygwin python (2.7 and 3.2) writes about 10x !!! faster than normal windows python (3.4)
# Writing 183.966 pages with coordinates out of 2.626.774 pages of the Dutch wikipedia 
# took 12 minutes versus 26 minutes (all on an I7-quadcore with an SSD disk)
# Also: DO NOT forget to "set PYTHONIOENCODING='utf-8'" on windows or other non-utf-8 environments.
#
# Usage from the folder dumps where your wikipedia or wikivoyage dumps reside
# $ python ../scripts/parse_wikidump.py wikipedia <language_code>
# or
# $ python ../scripts/parse_wikidump.py wikivoyage <language_code>
#
# example: $ python ../scripts/parse_wikidump.py wikipedia nl


import os, sys, bz2, gzip, csv, re, time, datetime, sqlite3, logging
import wikifunctions
# First check on version
if sys.version_info<(3,0,0):
#	from urllib import unquote
#	reload(sys)  
#	sys.setdefaultencoding('utf8')
	print('\n\nThis is a Python version 3.x.y script. It will not work with Python version 2\n\n')
	sys.exit()
else:
	from urllib.parse import unquote



######################### Some global settings and Constants ####################
SCRIPT_VERSION = "0.1"
# Set maximal characters for the text
MAX_CHARACTERS = 600
# What to generate
GENERATE_GPX = "NO"
GPX_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="dump_parse_wiki-' + SCRIPT_VERSION +'" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0"   xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n'

# Write a CSV
GENERATE_CSV = "YES" # YES or NO
GZIPPED_CVS = "NO" # YES or NO
CSV_HEADER = ['NAME','LATITUDE','LONGITUDE','COUNTRY','REGION','REMARKS','CONTENT']

GENERATE_OSM = "NO" # YES or NO
OSM_HEADER = "<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.5' generator='dump_parse_wiki-" + SCRIPT_VERSION + ">\n"

GENERATE_SQL = "NO" # YES or NO
GZIPPED_SQL = "YES" # YES or NO
Table_Fields = "(TITLE TEXT, LATITUDE FLOAT, LONGITUDE FLOAT, COUNTRY TEXT, REGION TEXT, REMARKS TEXT, CONTENT TEXT)"

# Writing the data to the sqlite database is preferred over ONLY writing to csv, even though that might be a lot faster.
# The csv output can contain (many) duplicates. We don't want that. In our database we can easily remove duplicates and then write 
# a csv from the database. 
CREATE_SQLITE = "NO" # YES or NO
SQLITE_DATABASE_PATH = '/opt/wikiscripts/sqlite/'  # This needs to be a full qualified path ending with a /

# English is our default code so we initiate everything as English
LANGUAGE_CODE = 'en'
ARTICLE_URL = "Article url: "
WIKI_PAGE_URL = "Wikipedia: "
# In the function below we set some language specific comments. This needs to be made a separate include file
# so people can easily add their own language statement
def language_specifics(lang_code):
	global LANGUAGE_CODE
	global ARTICLE_URL
	global WIKI_PAGE_URL
	WIKI_PAGE_URL = "Wikipedia: "
	# Adapt out fail safe english defaults to the correct ones
	if lang_code == "nl":
		LANGUAGE_CODE = 'nl'
		ARTICLE_URL = "Artikel url: "
	elif lang_code == "de":
		LANGUAGE_CODE = 'de'
		ARTICLE_URL = "Artikel url: "
	elif lang_code == "fr":
		LANGUAGE_CODE = 'fr'
		ARTICLE_URL = "URL de l'article: "
	elif lang_code == "no":
		LANGUAGE_CODE = 'no'
		ARTICLE_URL = "artikkelen url: "
	elif lang_code == "cs":
		LANGUAGE_CODE = 'cs'
		ARTICLE_URL = "článek url: "
	elif lang_code == "pl":
		LANGUAGE_CODE = 'pl'
		ARTICLE_URL = "artykuł url: "
	else:
		LANGUAGE_CODE = 'en'
		ARTICLE_URL = "Article url: "
		
		
# Below this you should not have to set or change anything
###########################################################################
def print_usage():
	print("\n\n\tYou should run this script from inside the folder where your wikidumps are downloaded.")
	print("\tThe default folder to run from according the setup of these scripts is \"dumps\".\n")
	print("\tThis script expects the type of wikidump, like wikipedia or wikivoyage,")
	print("\tand it expects a 2 character ISO-639-1 language_code.\n")
	print("\tlike: $ python ../scripts/parse_wikidump.py <wikitype> <language_code>\n")
	print("\tExamples:")
	print("\t\t$ python ../scripts/parse_wikidump.py wikipedia nl")
	print("\tor")
	print("\t\t$ python ../scripts/parse_wikidump.py wikivoyage en\n\n")
	sys.exit()

def check_commandline_parameters(sys_argv_params):
	#print(str(sys_argv_params))
	wikitype = ""
	language_code = ""
	if len(sys_argv_params) > 2:
		if str(sys_argv_params[1]) == "wikipedia":
			wikitype = "_wikipedia"
		elif str(sys_argv_params[1]) == "wikivoyage":
			wikitype = "_wikivoyage"
		else:
			print_usage()
		if len(sys_argv_params[2]) != 2:
			print_usage()
		else:
			language_code = sys_argv_params[2]
		#print(str(sys_argv_params[1]))
		#list_of_files.append(str(sys_argv_params[1]) + 'wiki-latest-pages-articles.xml')
	else:
		print_usage
	return wikitype, language_code


		
def parse_wiki_page(raw_page):
	#print(raw_page)
	page_string = ""
	text_string = ""
	# We do need a "state detector" to see whether we are in a <text......</text> area
	text_area = 0
	# We also need one for the optional infobox as we don't want that part
	infobox_area = 0
	web_string = ""
	for line in raw_page.splitlines():
		#print(str(line))
		# Take the text_area status into account
		if text_area == 1:
			# We are in the text area part
			# Check for some infobox info we don't want in the string but that we can use as "official" website for the wiki article
			# Temporarily disable. Sometime you'll find strange web addresses
			'''if ('| web' or '| website' or '| Website' or '| officiele_website =') in str(line).lower():
				#print(str(line))
				if '[http' in str(line).lower():
					wadr = re.search('\[(.*) ', line)
					if wadr:
						web_string = wadr.group(1)
					#print(wadr.group(1))
				elif '= http' in str(line).lower():
					wadr = re.search('= (.*)', line)
					if wadr:
						web_string = wadr.group(1)
					#print(wadr.group(1))
				elif '=http' in str(line).lower():
					wadr = re.search('=(.*)', line)
					if wadr:
						web_string = wadr.group(1)
					#print(wadr.group(1)) '''
			# Now check first whether we are in an infobox_area
			if infobox_area == 1:
				if '}}' in str(line):
					infobox_area = 0
			else:
				if '{{Infobox' in str(line):
					infobox_area = 1

				elif '</text>' in str(line):
					text_area = 0
					infobox_area = 0
					#page_string = text_only(page_string)					
				else:
					#page_string += str(line.replace('b"',''))
					text_string += str(line.replace('b"',''))

		if '<text xml:space="preserve">' in str(line):
			#page_string += '    <text>'
			text_string = ""
			text_area = 1
			if '{{Infobox' in str(line):
				infobox_area = 1
	# Return our page info in the normal way
	#return extlinkdata, text_string, web_string
	return text_string, web_string
## end of parse_wiki_page
###########################################################################


########### Start of main part ############
# Check correct usage
if len(sys.argv) > 2:
	wiki_type, language_code = check_commandline_parameters(sys.argv)
else:
	print_usage()

if wiki_type == "_wikipedia":
	wikipedia_file = language_code + 'wiki-latest-pages-articles.xml.bz2'
else:
	wikipedia_file = language_code + 'wikivoyage-latest-pages-articles.xml.bz2'

# Check if the file exists
if not os.path.exists(wikipedia_file):
	print("\n\nERROR:\n   The xml.bz2 file "+ wikipedia_file + " for the specified language: \"" + language_code + "\" does not exist!\n\n")
	sys.exit()

# Set some language specific settings (global variables)
language_specifics(language_code)
# Get the start time
start_time = datetime.datetime.now().replace(microsecond=0)
# heartbeat: check if script is not stuck
heart_beat = time.time()
str_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print('start time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
print("Working on language: " + LANGUAGE_CODE)
print('parse_wikidump.py: reading contents of: ' + wikipedia_file)
# Create log file
logging.basicConfig(filename='../logs/' + language_code + wiki_type + '.log',level=logging.DEBUG)
logging.info('start time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
# Do we want a GPX file?
if GENERATE_GPX == "YES":
	write_to_gpx_file = '../output/' + language_code + wiki_type + '.gpx'
	print('parse_wikidump.py: writing to GPX file: '+ write_to_gpx_file)
	gpx_file = open(write_to_gpx_file, 'w')
	gpx_file.write(GPX_HEADER)
	gpx_file.close()
	gpx_file = open(write_to_gpx_file, 'a')
# Do we want a CSV file?
if GENERATE_CSV == "YES":
	if GZIPPED_CVS == "YES":
		write_to_csv_file = '../output/' + language_code + wiki_type + '.csv.gz'
		gzipped_csv = gzip.open(write_to_csv_file, 'w')
		csv_file = csv.writer(gzipped_csv, delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)
	else:
		write_to_csv_file = '../output/' + language_code + wiki_type + '.csv'
		csv_file = csv.writer(open(write_to_csv_file, 'w'), delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)
	csv_file.writerow(CSV_HEADER)
	print('parse_wikidump.py: writing to CSV file: '+ write_to_csv_file)
	logging.info('parse_wikidump.py: writing to CSV file: '+ write_to_csv_file+'\n')
# Do we want an OSM file?
if GENERATE_OSM == "YES":
	node_counter = 0
	write_to_osm_file = '../output/' + language_code + wiki_type + '.osm'
	osm_file = open(write_to_osm_file, 'w')
	osm_file.write(OSM_HEADER)
	osm_file.close()
	print('parse_wikidump.py: also writing to OSM file: '+ write_to_osm_file)
	osm_file = open(write_to_osm_file, 'a')	
# Generate SQL
if GENERATE_SQL == "YES":
	if GZIPPED_SQL == "YES":
		write_to_sql_file = '../output/' + language_code + wiki_type + '.sql.gz'
		sql_file = gzip.open(write_to_sql_file, 'wb')
	else:
		write_to_sql_file = '../output/' + language_code + wiki_type + '.sql'
		sql_file = open(write_to_sql_file, 'wb')
	sql_file.write(bytes('drop table if exists ' + language_code + wiki_type + ';\n', 'UTF-8'))
	sql_file.write(bytes('create table ' + language_code + wiki_type + ' ' + Table_Fields + ';\n\n', 'UTF-8'))
	print('parse_wikidump.py: writing to SQL file: '+ write_to_sql_file)
	logging.info('parse_wikidump.py: writing to SQL file: '+ write_to_sql_file+'\n')
# Directly connect to sqlite database
#if CREATE_SQLITE == "YES":
#Doesn't matter whether whether we create sqlite database. We will always use the "in memory" externallinks database
# Create in memory database to speed up the process
wikidb = sqlite3.connect(':memory:') # create a memory database
cursor = wikidb.cursor()
SQLITE_DATABASE = SQLITE_DATABASE_PATH + language_code + 'wikipedia.db'
# Change to work in memory with the tables and write out at the end to disk
#wikidb = sqlite3.connect(SQLITE_DATABASE)
#cursor = wikidb.cursor()
sqlcommand = 'drop table if exists ' + language_code + wiki_type + ''
cursor.execute(sqlcommand)
sqlcommand = 'create table if not exists ' + language_code + wiki_type + ' ' + Table_Fields
cursor.execute(sqlcommand)
wikidb.commit()
# Now create in memory table <language_code>_externallinks.
# Could be done shorter but this is more compatible through python versions
cursor.execute("attach database '" + SQLITE_DATABASE + "' as filebased_db")
#print("attach database '" + SQLITE_DATABASE + "' as filebased_db")
cursor.execute("select sql from filebased_db.sqlite_master where type='table' and name='" + language_code + "_externallinks'")
#print("select sql from filebased_db.sqlite_master where type='table' and name='" + language_code + "_externallinks'")
sql_create_table = cursor.fetchone()[0]
cursor.execute(sql_create_table);
cursor.execute("insert into " + language_code + "_externallinks select * from filebased_db." + language_code + "_externallinks")
cursor.execute('CREATE INDEX ' + language_code + 'externallinks_TITLE on ' + language_code + '_externallinks(TITLE)')
#print(str(cursor.execute('.schema')))
# Now we detach the file based database and continue in memory
cursor.execute("detach database filebased_db")
wikidb.commit()
#cursor.execute('select count(title) from ' + language_code + '_externallinks')
#print(str(cursor.fetchone()))
print('parse_wikidump.py: Created table ' + language_code + '_externallinks in memory')
logging.info('parse_wikidump.py: Created table ' + language_code + '_externallinks in memory'+'\n')

if CREATE_SQLITE == "YES":
	print('parse_wikidump.py: inserting rows in table ' + language_code + wiki_type + ' in in memory database ')
	logging.info('parse_wikidump.py: inserting rows in table ' + language_code + wiki_type + ' in in memory database.'+'\n')

# Start reading from our wikipedia xml.bz2 file	
with bz2.BZ2File(wikipedia_file, 'r') as single_wikifile:
	# Initialize some variables so that we don't get incorrect values when they stay empty
	raw_page_string = ""
	text_string = ""
	web_string = ""
	pagecounter = 0
	totpagecounter = 0
	extlinkdata = []
	Country = ""
	Region = ""
	# We need to read line by line as we have massive files, sometimes multiple GBs
	for line in single_wikifile:
		if sys.version_info<(3,0,0):
			line = unicode(line, 'utf-8')
		else:
			line = line.decode("utf-8")
		raw_page_string += line
		if "</siteinfo>" in line:
			raw_page_string = ""
		elif "<title>" in line:
			Match = 0
			title_string = line.splitlines()
			extlinkdata = [None] * 6 # Create a list with 6 "None"s including our title which stays empty until proven "linked" via externallinks
			search_string = title_string[0].replace("    <title>","").replace("</title>","")
			try:
				cursor.execute('select * from ' + language_code + '_externallinks where title="'+search_string+'"')
				#print('select * from ' + language_code + '_externallinks where title="'+search_string+'"')
				row = cursor.fetchone()
				#print(row)
				if row[0] == search_string:
					extlinkdata[0] = search_string
					extlinkdata[1] = row[1]		# latitude
					extlinkdata[2] = row[2]		# longitude
					extlinkdata[3] = row[3]		# language
					extlinkdata[4] = row[4]		# poitype
					extlinkdata[5] = row[5]		# region
					Match = 1
					#print('Match: '+str(Match))
			except:
				pass
		elif "</page>" in str(line):
			# "heart beat check. Is this script still alife?
			check_pulse = time.time()
			if (check_pulse - heart_beat) > 600:   # 10 minutes -> 10*60 seconds
				print('Heart beat at: '+str(datetime.datetime.now().replace(microsecond=0))+'. Script still alive.')
				logging.info('Heart beat at: '+str(datetime.datetime.now().replace(microsecond=0))+'. Script still alive.')
				heart_beat = time.time()
			if Match == 1:
				text_string,web_string = parse_wiki_page(raw_page_string)
			# No do the final test: We need a title and a not-empty text
			if extlinkdata[0] != "" and extlinkdata[0] != None and text_string != "" and text_string != None:
				#title_string = extlinkdata[0].replace("    <title>","").replace("</title>","")
				title_string = extlinkdata[0]
				print('Matching ' + language_code + ' title: '+title_string)
				wikipediaurl = WIKI_PAGE_URL + 'http://' + language_code + '.wikipedia.org/wiki/' + title_string.replace(" ","_")
				latitude = extlinkdata[1]
				longitude = extlinkdata[2]
				articlelang = extlinkdata[3]
				poitype = extlinkdata[4]
				country_region = extlinkdata[5]
				if web_string != "":
					web_string = ARTICLE_URL + web_string
				text_string = wikifunctions.text_only(text_string)
				#limit to max "MAX_CHARACTERS" chars, remove leading \n and remove pipe/more separators
				text_string = text_string[:MAX_CHARACTERS].replace('\\n"','',1).replace('|','')
				# This might cut our string in the middle of a sentence. We don't want that
				# Find last full stop (period in English)
				p = text_string.rfind(".")
				# Get also rid of the percent encoded strings
				text_string = unquote(text_string[:p+1])
				remarks = '('+wikipediaurl
				#temporarily remove web_string. It contains all kind of links. I need to improve on this before using it
				#if web_string != "":
				#	remarks += ' ; '+web_string
				if poitype != "" and poitype != None:
					remarks += ' ; Type: '+poitype
				Country = ""
				Region = ""
				if country_region != "" and country_region != None:
					remarks += ' ; Country_Region: '+ country_region
					if len(country_region) >= 4:
						Country = country_region[:2]
						Region = country_region[3:]
					elif len(country_region) == 2:
						Country = country_region[:2]
						Region = ""
					#print('country_region: ' + country_region + ' Country: ' + Country + ' Region: ' + Region)
				remarks += ')'
				# Get rid of the percent encoded strings
				title_string = unquote(title_string)
				remarks = unquote(remarks)
				if GENERATE_GPX == "YES":
					gpx_file.write('<wpt lat="' + str(latitude) + '" lon="' + str(longitude) + '">\n')
					gpx_file.write('  <name>' + title_string + '</name>\n')
					gpx_file.write('  <desc>' + remarks +' ' + text_string + '</desc>\n')
					gpx_file.write('</wpt>\n')
				if GENERATE_CSV == "YES":
					csv_file.writerow([title_string, latitude, longitude, Country, Region, remarks, text_string])
				if GENERATE_OSM == "YES":
					node_counter += 1
					osm_file.write("<node id='" + str(node_counter) + "1' visible='true' lat='" + str(latitude) + "' lon='" + str(longitude) + "'>\n")
					osm_file.write("  <tag k='tourism' v='user'/>\n")
					osm_file.write("  <tag k='name' v='" + title_string + "'/>\n")
					if Country != "":
						osm_file.write("  <tag k='addr:country' v='" + Country + "'/>\n")
					if Region != "" and Country != "US":
						osm_file.write("  <tag k='province' v='" + Region + "'/>\n")
					elif  Region != "":
						osm_file.write("  <tag k='state' v='" + Region + "'/>\n")
					#if str(web_string) != "":
					#	osm_file.write("  <tag k='website' v='" + str(web_string) + "'/>\n")
					osm_file.write("  <tag k='note' v='" + remarks + ' ' + text_string + "'/>\n</node>\n")
				if GENERATE_SQL == "YES":
					sql_file.write(bytes('insert into ' + language_code + wiki_type + ' (TITLE, LATITUDE, LONGITUDE, COUNTRY, REGION, REMARKS, CONTENT) values ("' + title_string + '","' + str(latitude) + '","' + str(longitude) + '","' + Country + '","' + Region  + '","' + remarks + '","' + text_string + '");\n', 'UTF-8'))
				if CREATE_SQLITE == "YES":
					cursor.execute('insert into ' + language_code + wiki_type + ' (TITLE, LATITUDE, LONGITUDE, COUNTRY, REGION, REMARKS, CONTENT) values ("' + title_string + '","' + str(latitude) + '","' + str(longitude) + '","' + Country + '","' + Region  + '","' + remarks + '","' + text_string + '");')
					# For testing we want immediate commits
					#wikidb.commit()
				pagecounter += 1
				raw_page_string = ""
				if pagecounter == 2500:
					if CREATE_SQLITE == "YES":
						# Do a database commit every 2500 rows
						wikidb.commit()
					totpagecounter += pagecounter
					pagecounter = 0
					print('\nProcessed pages ' + str(totpagecounter) + '. Elapsed time: ' + str(datetime.datetime.now().replace(microsecond=0) - start_time))
					logging.info('\nProcessed pages ' + str(totpagecounter) + '. Elapsed time: ' + str(datetime.datetime.now().replace(microsecond=0) - start_time)+'\n')
		elif "</mediawiki>" in str(line):
			print('\nTotal processed pages ' + str(totpagecounter + pagecounter) + '.')
			logging.info('\nTotal processed pages ' + str(totpagecounter + pagecounter) + '.')
	#print('\n\nNow writing the ' + write_to_gpx_file + ' file')

# Close everything nicely, whether we have a corrupt bzip, EOF error or whatever issue
if GENERATE_GPX == "YES":
	gpx_file.write('</gpx>')
	gpx_file.close()
if GENERATE_CSV == "YES" and GZIPPED_CVS == "YES":
	gzipped_csv.close()
if GENERATE_OSM == "YES":
	osm_file.close()
if GENERATE_SQL == "YES":
	sql_file.write(bytes('\n\ncreate index ' + language_code + 'TITLE on ' + language_code + wiki_type + '(TITLE);\n\n', 'UTF-8'))
	sql_file.close()
if CREATE_SQLITE == "YES":
	cursor.execute('drop table '+language_code + '_externallinks')
	cursor.execute("attach database '" + SQLITE_DATABASE + "' as filebased_db")
	cursor.execute('drop table if exists filebased_db.' + language_code + wiki_type + '')
	cursor.execute('create table if not exists filebased_db.' + language_code + wiki_type + ' ' + Table_Fields)
	wikidb.commit()
	cursor.execute('insert into filebased_db.' + language_code + wiki_type + ' select * from ' + language_code + wiki_type + '')
	wikidb.commit()
	cursor.execute('create index if not exists filebased_db.' + language_code + 'TITLE on ' + language_code + wiki_type + '(TITLE);')
	cursor.execute("detach database filebased_db")
	wikidb.close()
	
	
	
	
str_end_time = time.strftime("%Y-%m-%d %H:%M:%S")
end_time = datetime.datetime.now().replace(microsecond=0)	
print('Start time: ' + str_start_time + '\n')
print('End time: ' + str_end_time + '\n')
logging.info('End time: ' + str_end_time + '\n')
print('Total time: ' + str(end_time - start_time))
logging.info('Total time: ' + str(end_time - start_time)+'\n')
logging.shutdown()

#End of file
