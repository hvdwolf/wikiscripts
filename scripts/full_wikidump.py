#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.8, 2015-04-13, Harry van der Wolf
# This file must be used on a compressed xml.bz file
# Usage: python full_wikidump.py <iso-639-1 language code>
# example: python full_wikidump.py en
# Note: wikipedia works per language!, not per country. 
# See http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes for those codes.
# As an example "python full_wikidump.py de" will convert the German language version, which is of course for every German speaker/reader.
# This script will always write a GPX file and can optionally write a CSV and/or OSM file.

# Note: do not attempt some "buffered" writes to memory and then once every xyz lines to file.
# That is much slower than simple write line by line
#
# Note 2 (windows): cygwin python (2.7 and 3.2) writes about 10x !!! faster than normal windows python (3.4)
# Writing 183.966 pages with coordinates out of 2.626.774 pages of the Dutch wikipedia 
# took 12 minutes versus 26 minutes (all on an I7-quadcore with an SSD disk)
# Also: DO NOT forget to "set PYTHONIOENCODING='utf-8'" on windows or other non-utf-8 environments.


import os, sys, bz2, gzip, csv, re, time, datetime, sqlite3
import wikifunctions

p_version = sys.version_info

######################### Some global settings and Constants ####################
SCRIPT_VERSION = "0.8"
# Set maximal characters for the text
MAX_CHARACTERS = 600
# Whether to generate GPX, CSV and OSM files
GENERATE_GPX = "NO"
GPX_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n<gpx version="1.0" creator="dump_parse_wiki-' + SCRIPT_VERSION +'" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.topografix.com/GPX/1/0"   xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">\n'

GENERATE_CSV = "NO" # YES or NO
GZIPPED_CVS = "YES" # YES or NO
CSV_HEADER = ['NAME','WIKIPEDIAURL','URL','CONTENT']

GENERATE_SQL = "YES" # YES or NO
GZIPPED_SQL = "YES" # YES or NO
Table_Fields = "(TITLE TEXT, WIKIPEDIAURL TEXT, URL TEXT, CONTENT TEXT)"

GENERATE_OSM = "NO" # YES or NO
OSM_HEADER = "<?xml version='1.0' encoding='UTF-8'?>\n<osm version='0.5' generator='dump_parse_wiki-" + SCRIPT_VERSION + ">\n"

CREATE_SQLITE = "YES" # YES or NO
SQLITE_DATABASE = '/cygdrive/d/wikiscripts/sqlite/wikipedia'  # This needs to be the database via a full qualified path

# English is our default code so we initiate everything as English
LANGUAGE_CODE = 'en'
ARTICLE_URL = "Article url: "
WIKI_PAGE_URL = "Wikipedia page: "
COORDINATES_FORMAT = "{{Coord"
# And in the function below we adapt
def language_specifics(lang_code):
	global LANGUAGE_CODE
	global ARTICLE_URL
	global WIKI_PAGE_URL
	global COORDINATES_FORMAT
	WIKI_PAGE_URL = "Wikipedia: "
	# Adapt out fail safe english defaults to the correct ones
	if lang_code == "nl":
		LANGUAGE_CODE = 'nl'
		ARTICLE_URL = "Artikel url: "
		#WIKI_PAGE_URL = "Wikipedia pagina: "
	elif lang_code == "de":
		LANGUAGE_CODE = 'de'
		ARTICLE_URL = "Artikel url: "
		#WIKI_PAGE_URL = "Wikipedia Seite: "
	elif lang_code == "fr":
		LANGUAGE_CODE = 'fr'
		ARTICLE_URL = "URL de l'article: "
		#WIKI_PAGE_URL = "page Wikipedia: "
	elif lang_code == "no":
		LANGUAGE_CODE = 'no'
		ARTICLE_URL = "artikkelen url: "
		#WIKI_PAGE_URL = "Wikipedia nettside: "
	elif lang_code == "cs":
		LANGUAGE_CODE = 'cs'
		ARTICLE_URL = "článek url: "
		#WIKI_PAGE_URL = "Wikipedia webová stránka: "
	elif lang_code == "pl":
		LANGUAGE_CODE = 'pl'
		ARTICLE_URL = "artykuł url: "
		
		
# Below this you should not have to set or change anything
###########################################################################


		
def parse_wiki_page(raw_page):
	#print(raw_page)
	page_string = ""
	# We do need a "state detector" to see whether we are in a <text......</text> area
	text_area = 0
	# We also need one for the optional infobox as we don't want that part
	infobox_area = 0
	web_string = ""
	for line in raw_page.splitlines():
		#print(str(line))
		# Just follow the chronological order in the file: <page><title></title><text></text></page>
		# However take the text_area status into account
		if text_area == 1:
			# We are in the text area part
			# Check for some infobox info we don't want in the string but that we can use
			if ('| web' or '| website' or '| Website' or '| officiele_website =') in str(line).lower():
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
					#print(wadr.group(1))
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
		#if '<page>' in str(line):
		#	page_string += '<page>\n'
		if '<title>' in str(line):
			#page_string += line + '\n'
			title_string = line
		if '<text xml:space="preserve">' in str(line):
			#page_string += '    <text>'
			text_string = ""
			text_area = 1
			if '{{Infobox' in str(line):
				infobox_area = 1
	# And finally return our moderate page string
	return title_string, text_string, web_string
## end of parse_wiki_page
###########################################################################


# Start of main part
if len(sys.argv) > 1:
	#print(str(sys.argv[1]))
	#list_of_files.append(str(sys.argv[1]) + 'wiki-latest-pages-articles.xml')
	wikipedia_file = str(sys.argv[1]) + 'wiki-latest-pages-articles.xml.bz2'
	#bz_wikipedia_file = bz2.BZ2File(str(sys.argv[1]) + 'wiki-latest-pages-articles.xml.bz2', 'rb')
else:
	print('No parameter given. You need to give the 2-character country code in lower case.')
	sys.exit()
	
# Set some language specific settings (global variables)
file_prefix = str(sys.argv[1])
language_specifics(wikipedia_file[:2])
# Get the start time
start_time = datetime.datetime.now().replace(microsecond=0)
str_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print('start time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
print("Working on language: " + LANGUAGE_CODE)
print('full_wikidump.py: reading contents of: ' + wikipedia_file)
if GENERATE_GPX == "YES":
	write_to_gpx_file = file_prefix + '_wikipedia.gpx'
	print('full_wikidump.py: writing to GPX file: '+ write_to_gpx_file)
	gpx_file = open(write_to_gpx_file, 'wb')
	gpx_file.write(GPX_HEADER)
	gpx_file.close()
	gpx_file = open(write_to_gpx_file, 'a')
# Do we want a CSV file?
if GENERATE_CSV == "YES":
	if GZIPPED_CVS == "YES":
		write_to_csv_file = file_prefix + '_wikipedia.csv.gz'
		gzipped_csv = gzip.open(write_to_csv_file, 'wb')
		csv_file = csv.writer(gzipped_csv, delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)
	else:
		write_to_csv_file = file_prefix + '_wikipedia.csv'
		csv_file = csv.writer(open(write_to_csv_file, 'wb'), delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)
	csv_file.writerow(CSV_HEADER)
	print('full_wikidump.py: writing to CSV file: '+ write_to_csv_file)
# Generate SQL
if GENERATE_SQL == "YES":
	if GZIPPED_SQL == "YES":
		write_to_sql_file = file_prefix + '_wikipedia.sql.gz'
		sql_file = gzip.open(write_to_sql_file, 'wb')
	else:
		write_to_sql_file = file_prefix + '_wikipedia.sql'
		sql_file = open(write_to_sql_file, 'wb')
	sql_file.write('drop table if exists ' + file_prefix + '_wikipedia;\n')
	sql_file.write('create table ' + file_prefix + '_wikipedia ' + Table_Fields + ';\n\n')
	print('full_wikidump.py: writing to SQL file: '+ write_to_sql_file)
# Directly conect to sqlite database
if CREATE_SQLITE == "YES":
	wikidb = sqlite3.connect(SQLITE_DATABASE)
	cursor = wikidb.cursor()
	sqlcommand = 'drop table if exists ' + file_prefix + '_wikipedia'
	cursor.execute(sqlcommand)
	sqlcommand = 'create table if not exists ' + file_prefix + '_wikipedia ' + Table_Fields
	cursor.execute(sqlcommand)
	wikidb.commit()
	print('full_wikidump.py: inserting rows for table ' + file_prefix + '_wikipedia in database ' + SQLITE_DATABASE)
	#print(sqlcommand)
# Do we want an OSM file?
if GENERATE_OSM == "YES":
	node_counter = 0
	write_to_osm_file = file_prefix + '_wikipedia.osm'
	osm_file = open(write_to_osm_file, 'w')
	osm_file.write(OSM_HEADER)
	osm_file.close()
	print('full_wikidump.py: also writing to OSM file: '+ write_to_osm_file)
	osm_file = open(write_to_osm_file, 'a')	

#with codecs.open(wikipedia_file, 'r', 'utf-8') as single_wikifile:
with bz2.BZ2File(wikipedia_file, 'r') as single_wikifile:
#	with codecs.open('utf-8')(bz2.BZ2File('wikipedia_file)) as single_wikifile:
	#rows = single_wiki.readlines()
	#page_string = ""
	raw_page_string = ""
	pagecounter = 0
	totpagecounter = 0
	# We need to read line by line as we have massive files, sometimes multiple GBs
	for line in single_wikifile:
		# We need to add a \n to make the lines separate
		raw_page_string += str(line).replace("b'","") + str('\n')
		#print(str(line).encode('utf-8'))
		if "</siteinfo>" in str(line):
			#raw_page_string = raw_page_string.replace("\n'","")
			#text_file.write(raw_page_string)
			raw_page_string = ""
		if "</page>" in str(line):
			# test for coordinates
			# EN, NL, DE, NO: {{Coord ; CS: | zeměpisná ; FR: coordonnées_capitale
			# This needs better finetuning in the parse functions
			if "<ns>0</ns>" in raw_page_string:
				# And now we need to remove the \n' again. Obviously I'm doing something stupid
				raw_page_string = raw_page_string.replace("\\n'","")
				#raw_page_string = str(re.sub(r'{{Infobox.*?}}',raw_page_string,1))
				#print(raw_page_string)
				title_string,text_string,web_string = parse_wiki_page(raw_page_string)
				# Do some post processing
				# final test
				title_string = title_string.replace("    <title>","").replace("</title>","")
				wikipediaurl = WIKI_PAGE_URL + 'http://' + LANGUAGE_CODE + '.wikipedia.org/wiki/' + title_string.replace(" ","_")
				if web_string != "":
					web_string = ARTICLE_URL + web_string
				text_string = wikifunctions.text_only(text_string)
				# convert some HTML remnants DO NOT USE! BREAKS SOME GPX STRINGS
				#text_string = replace_html_codes(text_string, HTML_DICTIONARY)
				#limit to max "MAX_CHARACTERS" chars, remove leading \n and remove pipe/more separators
				text_string = text_string[:MAX_CHARACTERS].replace('\\n"','',1).replace('|','')
				# This might cut our sting in the middle of a sentence. We don't want that
				# Find last full stop (period in English)
				p = text_string.rfind(".")
				text_string = text_string[:p+1]
				#text_file.write(raw_page_string)
				# gpx_file will always be written
				#gpx_file.write(text_only(page_string))
				if GENERATE_GPX == "YES":
					gpx_file.write('<wpt lat="' + str(latitude) + '" lon="' + str(longitude) + '">\n')
					gpx_file.write('  <name>' + title_string + '</name>\n')
					gpx_file.write('  <desc>' + wikipediaurl + '; ' + web_string + '; ' + text_string + '</desc>\n')
					gpx_file.write('</wpt>\n')
				if GENERATE_CSV == "YES":
					#print('latitude: ' + str(latitude) + '  longitude: ' + str(longitude))
					#csv_file.write('"' + title_string + '";"' + str(latitude) + '";"' + str(longitude) + '";"' + wikipediaurl + '. ";"' + web_string + '. ";"' + text_string + '"\n')
					csv_file.writerow([title_string, wikipediaurl, web_string, text_string])
				if GENERATE_SQL == "YES":
					sql_file.write('insert into ' + file_prefix + '_wikipedia (TITLE, WIKIPEDIAURL, URL, CONTENT) values ("' + title_string + '","' + wikipediaurl + '","' + web_string + '","' + text_string + '");\n')
				if CREATE_SQLITE == "YES":
					sqlcommand = 'insert into ' + file_prefix + '_wikipedia (TITLE, WIKIPEDIAURL, URL, CONTENT) values ("' + title_string + '","' + wikipediaurl + '","' + web_string + '","' + text_string + '");'
					#print(sqlcommand)
					cursor.execute(sqlcommand)
				if GENERATE_OSM == "YES":
					node_counter += 1
					osm_file.write("<node id='" + str(node_counter) + "1' visible='true' lat='" + str(latitude) + "' lon='" + str(longitude) + "'>\n")
					osm_file.write("  <tag k='tourism' v='user'/>\n")
					osm_file.write("  <tag k='name' v='" + str(title_string) + "'/>\n")
					if str(web_string) != "":
						osm_file.write("  <tag k='website' v='" + str(web_string) + "'/>\n")
					osm_file.write("  <tag k='note' v='" + text_string + "'/>\n</node>\n")
				pagecounter += 1
				raw_page_string = ""
				#page_string = ""
				#pagecounter += 1
				if pagecounter == 5000:
					if CREATE_SQLITE == "YES":
						# Do a databse commit every 5000 rows
						wikidb.commit()
					totpagecounter += pagecounter
					pagecounter = 0
					print('\nProcessed pages ' + str(totpagecounter) + '. Elapsed time: ' + str(datetime.datetime.now().replace(microsecond=0) - start_time))
			else:
				# No <ns>0<ns> page
				raw_page_string = ""
		if "</mediawiki>" in str(line):
			if GENERATE_GPX == "YES":
				gpx_file.write('</gpx>')
				gpx_file.close()
			if GENERATE_CSV == "YES" and GZIPPED_CVS == "YES":
				#csv_file.close()
				gzipped_csv.close()
			if GENERATE_SQL == "YES":
				sql_file.write('\n\ncreate index ' + file_prefix + 'TITLE on ' + file_prefix + '_wikipedia(TITLE);\n\n')
				sql_file.write('drop view if exists ' + file_prefix + '_wikipedia_view;\n')
				sql_file.write('create view if not exists ' + file_prefix + '_wikipedia_view as select title, lat,lon,"("||wikipediaurl||"; "||url||"; Country/Region: "||Country||"/"||SubRegion||")" as comment,content from ' + file_prefix + '_wikipedia inner join wp_coords_red0 on wp_coords_red0.titel=' + file_prefix + '_wikipedia.title and lang="' + file_prefix +'";\n')
				sql_file.close()
			if GENERATE_OSM == "YES":
				osm_file.close()
			if CREATE_SQLITE == "YES":
				sqlcommand = 'create index ' + file_prefix + 'TITLE on ' + file_prefix + '_wikipedia(TITLE);'
				cursor.execute(sqlcommand)
				sqlcommand = 'create view if not exists ' + file_prefix + '_wikipedia_view as select title, lat,lon,"("||wikipediaurl||"; "||url||"; Country/Region: "||Country||"/"||SubRegion||")" as comment,content from ' + file_prefix + '_wikipedia inner join wp_coords_red0 on wp_coords_red0.titel=' + file_prefix + '_wikipedia.title and lang="' + file_prefix +'";'
				cursor.execute(sqlcommand)
				wikidb.close()
			print('\nTotal processed pages ' + str(totpagecounter + pagecounter) + '.')
	#print('\n\nNow writing the ' + write_to_gpx_file + ' file')

str_end_time = time.strftime("%Y-%m-%d %H:%M:%S")
end_time = datetime.datetime.now().replace(microsecond=0)	
print('Start time: ' + str_start_time + '\n')
print('End time: ' + str_end_time + '\n')
print('Total time: ' + str(end_time - start_time))

#End of file
