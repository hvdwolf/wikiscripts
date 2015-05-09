#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version 0.1, 2015-04-26, Harry van der Wolf
# This file must be used on a compressed sql.gz file
# Usage: python externallinks.py <iso-639-1 language code>
# example: python externallinks.py en
# Note: wikivoyage works per language!, not per country. 
# See http://en.wikivoyage.org/wiki/List_of_ISO_639-1_codes for those codes.
# As an example "python externallinks.py de" will read the German language version, which is of course for every German speaker/reader.
# It will create an sqlite database record for every externallink having geohack.php in the url meaning that it has coordinates

# Note: do not attempt some "buffered" writes to memory and then once every xyz lines to file.
# That is much slower than simple write line by line
#
# Note 2 (windows): cygwin python (2.7 and 3.2) writes about 10x !!! faster than normal windows python (3.4)
# Writing 183.966 pages with coordinates out of 2.626.774 pages of the Dutch wikivoyage 
# took 12 minutes versus 26 minutes (all on an I7-quadcore with an SSD disk)
# Also: DO NOT forget to "set PYTHONIOENCODING='utf-8'" on windows or other non utf-8 environments.


import os, sys, gzip, re, time, datetime, sqlite3
import wikifunctions
if sys.version_info<(3,0,0):
	from urllib import unquote
else:
	from urllib.parse import unquote

######################### Some global settings and Constants ####################
SCRIPT_VERSION = "0.1"
# Whether to generate an SQL file
GENERATE_SQL = "NO" # YES or NO
GZIPPED_SQL = "NO" # YES or NO
Table_Fields = "(Title text, latitude float, longitude float, language text, poitype text, region text)"

# Directly store in sqlite database
CREATE_SQLITE = "YES" # YES or NO
SQLITE_DATABASE_PATH = '/cygdrive/d/wikiscripts/sqlite/wikipedia'  # This needs to be a full qualified path

		
		
# Below this you should not have to set or change anything
###########################################################################

def get_coordinates_type_region(params_list):
	latitude = 0
	longitude = 0
	poitype = ""
	region = ""
	#print(str(params_list))
	# See if we have poi types and regions
	for item in params_list:
		if item.startswith("type:"):
			poitype = item.replace("type:","")
		elif item.startswith("region:"):
			region = item.replace("region:","")
	# Now try to get the coordinates
	# Note that the last item before the N, S, E, W can be a "float" but having a "," instead of a "."
	# Note also that this last item can also be incorrect sometimes not being a number: so check for it
	if len(params_list) >=8:
		if params_list[7] == "E" or params_list[7] == "W": # Something like |46|8|2.15|N|64|51|42.86|W|etcetera
			if (not wikifunctions.IsACharString(params_list[0]) and not wikifunctions.IsACharString(params_list[1]) and not wikifunctions.IsACharString(params_list[2])):
				latitude = float(params_list[0]) + float(params_list[1])/float(60) + float(params_list[2].replace(",","."))/float(3600)
				if params_list[3] == 'S':
					latitude = -(latitude)
			else:
				latitude = ""
			if (not wikifunctions.IsACharString(params_list[4]) and not wikifunctions.IsACharString(params_list[5]) and not wikifunctions.IsACharString(params_list[6])):
				longitude = float(params_list[4]) + float(params_list[5])/float(60) + float(params_list[6].replace(",","."))/float(3600)
				if params_list[7] == 'W':
					longitude = -(longitude)
			else:
				longitude = ""
		elif params_list[5] == "E" or params_list[5] == "W": # Something like 46|8|N|64|51|W|etcetera with extended region, type, etc.
			if (not wikifunctions.IsACharString(params_list[0]) and not wikifunctions.IsACharString(params_list[1])):
				latitude = float(params_list[0]) + float(params_list[1].replace(",","."))/float(60)
				if params_list[2] == 'S':
					latitude = -(latitude)
			else:
				latitude = ""
			if (not wikifunctions.IsACharString(params_list[3]) and not wikifunctions.IsACharString(params_list[4])):
				longitude = float(params_list[3]) + float(params_list[4].replace(",","."))/float(60)
				if params_list[5] == 'W':
					longitude = -(longitude)
			else:
				longitude = ""
	elif len(params_list) >=6:
		if params_list[5] == "E" or params_list[5] == "W": # Something like 46|8|N|64|51|W|etcetera
			if (not wikifunctions.IsACharString(params_list[0]) and not wikifunctions.IsACharString(params_list[1])):
				latitude = float(params_list[0]) + float(params_list[1].replace(",","."))/float(60)
				if params_list[2] == 'S':
					latitude = -(latitude)
			else:
				latitude = ""
			if (not wikifunctions.IsACharString(params_list[3]) and not wikifunctions.IsACharString(params_list[4])):
				longitude = float(params_list[3]) + float(params_list[4].replace(",","."))/float(60)
				if params_list[5] == 'W':
					longitude = -(longitude)
			else:
				longitude = ""
		elif params_list[3] == "E" or params_list[3] == "W": # Something like 46.123|N|64.987|W|etcetera with longer region, type etc.
			if not wikifunctions.IsACharString(params_list[0]):
				latitude = float(params_list[0].replace(",","."))
				if params_list[1] == 'S':
					latitude = -(latitude)
			else:
				latitude = ""
			if not wikifunctions.IsACharString(params_list[2]):
				longitude = float(params_list[2].replace(",","."))
				if params_list[3] == 'W':
					longitude = -(longitude)
			else:
				longitude = ""
	elif len(params_list) >=4:
		if params_list[3] == "E" or params_list[3] == "W": # Something like 46|N|64|W|etcetera or like 46.123|N|64.987|W|etcetera
			if not wikifunctions.IsACharString(params_list[0]):
				latitude = float(params_list[0].replace(",","."))
				if params_list[1] == 'S':
					latitude = -(latitude)
			else:
				latitude = ""
			if not wikifunctions.IsACharString(params_list[2]):
				longitude = float(params_list[2].replace(",","."))
				if params_list[3] == 'W':
					longitude = -(longitude)
			else:
				longitude = ""
	#for item in params_list:
	#	print(str(len(params_list)))
	#print('latitude: ' + str(latitude) + '; longitude: ' + str(longitude))
	return latitude, longitude, poitype, region
###########################################################################


# Start of main part
if len(sys.argv) > 1:
	#print(str(sys.argv[1]))
	#list_of_files.append(str(sys.argv[1]) + 'wikivoyage-latest-pages-articles.xml')
	externallinks_file = str(sys.argv[1]) + 'wiki-latest-externallinks.sql.gz'
	# Check if the file exists
	if not os.path.exists(externallinks_file):
		print("\n\nERROR:\n   The sql.gz file "+ externallinks_file + " for the specified language: \"" + str(sys.argv[1]) + "\" does not exist!\n\n")
		sys.exit()
else:
	print('No parameter given. You need to give the 2-character country code in lower case.')
	sys.exit()
	
# Set some language specific settings (global variables)
file_prefix = str(sys.argv[1])
# Get the start time
start_time = datetime.datetime.now().replace(microsecond=0)
str_start_time = time.strftime("%Y-%m-%d %H:%M:%S")
print('start time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\n')
print("Working on language: " + file_prefix)
print('externallinks.py: reading contents of: ' + externallinks_file)

# Generate SQL
if GENERATE_SQL == "YES":
	if GZIPPED_SQL == "YES":
		write_to_sql_file = file_prefix + '_externallinks.sql.gz'
		if sys.version_info<(3,0,0):
			sql_file = gzip.open(write_to_sql_file, 'wt')
		else:
			sql_file = gzip.open(write_to_sql_file, 'w+',encoding='utf-8')
	else:
		write_to_sql_file = file_prefix + '_externallinks.sql'
		if sys.version_info<(3,0,0):
			sql_file = open(write_to_sql_file, 'wt')
		else:
			sql_file = open(write_to_sql_file, 'w+',encoding='utf-8')
	sql_file.write('drop table if exists ' + file_prefix + '_externallinks;\n')
	sql_file.write('create table ' + file_prefix + '_externallinks ' + Table_Fields + ';\n\n')
	print('externallinks.py: writing to SQL file: '+ write_to_sql_file)
# Directly connect to sqlite database
if CREATE_SQLITE == "YES":
	SQLITE_DATABASE = SQLITE_DATABASE_PATH + file_prefix + 'wikipedia.db'
	wikidb = sqlite3.connect(SQLITE_DATABASE)
	cursor = wikidb.cursor()
	sqlcommand = 'drop table if exists ' + file_prefix + '_externallinks'
	cursor.execute(sqlcommand)
	sqlcommand = 'create table if not exists ' + file_prefix + '_externallinks ' + Table_Fields
	cursor.execute(sqlcommand)
	wikidb.commit()
	print('externallinks.py: inserting rows for table ' + file_prefix + '_externallinks in database ' + SQLITE_DATABASE)

with gzip.open(externallinks_file, 'r') as single_externallinksfile:
	linecounter = 0
	totlinecounter = 0
	filelinecounter = 0
	# We need to read line by line as we have massive files, sometimes multiple GBs
	for line in single_externallinksfile:
		if sys.version_info<(3,0,0):
			line = unicode(line, 'utf-8')
		else:
			line = line.decode("utf-8")
		if "INSERT INTO" in line:
			insert_statements = line.split("),(")
			for statement in insert_statements:
				filelinecounter += 1
				#if ("geohack.php?" in statement) and (("pagename" in statement) or ("src=" in statement)): 
				# src can also be in the line, but is different and we leave it out for now
				if ("geohack.php?" in statement) and ("pagename" in statement) and ("params" in statement):
					language = ""
					region = ""
					poitype = ""
					content = re.findall(r'.*?pagename=(.*?)\'\,\'',statement,flags=re.IGNORECASE)
					if len(content) > 0: # We even need this check due to corrupted lines
						splitcontent = content[0].split("&")
						title = splitcontent[0]
						#title = title.decode('utf8')
						for subcontent in splitcontent:
							if "language=" in subcontent:
								language = subcontent.replace("language=","")
								#print('taal is: ' + language)
							if "params=" in subcontent:
								params_string = subcontent.replace("params=","").split("_")
								latitude,longitude,poitype,region = get_coordinates_type_region(params_string)
						if ( str(latitude) != "" and str(longitude) != "" and  (str(latitude) != "0") or (str(longitude) != "0")):
							if GENERATE_SQL == "YES":
								sql_file.write('insert into ' + file_prefix + '_externallinks values ("' + unquote(title) + '","' + str(latitude) + '","' + str(longitude) + '","' + language + '","' + poitype + '","' + region + '");\n')
							if CREATE_SQLITE == "YES":
								try:  #Sometimes we run into some weird unicode title that sqlite really can't process
									sqlcommand = 'insert into ' + file_prefix + '_externallinks values ("' + unquote(title) + '","' + str(latitude) + '","' + str(longitude) + '","' + language + '","' + poitype + '","' + region +'");'
									cursor.execute(sqlcommand)
								except:
									pass
							linecounter += 1
							if linecounter == 10000:
								if CREATE_SQLITE == "YES":
									# Do a database commit every 10000 rows
									wikidb.commit()
								totlinecounter += linecounter
								linecounter = 0
								print('\nProcessed ' + str(totlinecounter) + ' lines out of ' + str(filelinecounter) + ' sql line statements. Elapsed time: ' + str(datetime.datetime.now().replace(microsecond=0) - start_time))
		

	if GENERATE_SQL == "YES":
		sql_file.write('\n\ncreate index ' + file_prefix + 'externallinks_TITLE on ' + file_prefix + '_externallinks(TITLE);\n\n')
		sql_file.write('\n\ncreate index ' + file_prefix + 'externallinks_lat_lon on ' + file_prefix + '_externallinks(Latitude, Longitude);\n\n')
		# remove all the double records
		sql_file.write('\n\ndelete from ' + file_prefix + '_externallinks where rowid not in (select max(rowid) from ' + file_prefix + '_externallinks group by title);\n\n')
		sql_file.close()
	if CREATE_SQLITE == "YES":
		print('\nDone importing.\nCreating indexes')
		sqlcommand = 'create index ' + file_prefix + 'externallinks_TITLE on ' + file_prefix + '_externallinks(TITLE);'
		cursor.execute(sqlcommand)
		sqlcommand = 'create index ' + file_prefix + 'externallinks_lat_lon on ' + file_prefix + '_externallinks(Latitude, Longitude);'
		cursor.execute(sqlcommand)
		print('Removing all double records and "vacuum" (shrink) the database afterwards')
		sqlcommand = 'delete from ' + file_prefix + '_externallinks where rowid not in (select max(rowid) from ' + file_prefix + '_externallinks group by title);'
		cursor.execute(sqlcommand)
		wikidb.commit()
		# Clean up some empty database space. Very imported for the big languages
		cursor.execute('VACUUM')
		wikidb.close()
	print('\nTotal processed ' + str(totlinecounter + linecounter) + ' lines out of ' + str(filelinecounter) + ' sql line statements.')

str_end_time = time.strftime("%Y-%m-%d %H:%M:%S")
end_time = datetime.datetime.now().replace(microsecond=0)	
print('Start time: ' + str_start_time + '\n')
print('End time: ' + str_end_time + '\n')
print('Total time: ' + str(end_time - start_time))

#End of file
