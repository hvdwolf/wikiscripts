#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, bz2, csv, re, time, datetime

# helper pythons script en_coordinates
######################### function modules ################################

# Media and categories; the codes for these differ per language.
# We have the most popular ones (>900.000 articles as of July 2012) here,
# as well as Latin, which is useful for testing.
# Add other languages as required.
_MEDIA_CAT = """
  [Ii]mage|[Cc]ategory      # English
 |[Aa]rchivo                # Spanish
 |[Ff]ile                   # English, Italian
 |[CcKk]at[ée]gor[íi][ea]   # Dutch, German, French, Italian, Spanish, Polish, Latin
 |[Bb]estand                # Dutch
 |[Bb]ild                   # German
 |[Ff]icher                 # French
 |[Pp]lik                   # Polish
 |[Ff]asciculus             # Latin
"""
#Unwanted
#  | \&lt;ref .*?\> .*? \&quot; /\&gt;
#  | \&lt;br.*? \&gt;

_UNWANTED = re.compile(r"""
  (:?
    \{\{ .*? \}\}                           # templates
  | \| .*? \n                               # left behind from templates
  | \}\}                                    # left behind from templates
  | <!-- .*? -->
  | <div .*?> .*? </div>
  | <math> .*? </math>
  | <nowiki> .*? </nowiki>
  | <ref .*?> .*? </ref>
  | \&lt;ref\&gt;.*?\&lt;/ref\&gt;
  | \&lt;ref .*?\> .*? \&quot; /\&gt;
  | \&lt;br.*? \&gt;
  | <ref .*?/>
  | <span .*?> .*? </span>
  | \[\[ (:?%s): (\[\[.*?\]\]|.)*? \]\]
  | \[\[ [a-z]{2,}:.*? \]\]                 # interwiki links
  | =+                                      # headers
  | \{\| .*? \|\}
  | \[\[ (:? [^]]+ \|)?
  | \]\]
  | '{2,}
  | \&quot;
  | \&amp;
  )
""" % _MEDIA_CAT,
re.DOTALL | re.MULTILINE | re.VERBOSE)


def text_only(text):
    return _UNWANTED.sub("", text)
# Functions above copied from https://github.com/larsmans/wiki-dump-tools


def typeofvalue(text):
# Try to find if it is a float. Used for the coordinates
	try:
		float(text)
		return float
	except ValueError:
		pass
		return "string"

def IsANumber(text):
# Alsmost equal to typeofvalue
	try:
		float(text)
		return True
	except ValueError:
		pass
		return False
def IsACharString(text):
# Opposite of IsANumber
	try:
		float(text)
		return False
	except ValueError:
		pass
		return True

		
def string_float_int(x):
# Another tester for string or floats. We can't use this or coordinates as we are always starting from a string
# so that check will alsways be: "string"
	if isinstance(x, int):
		#print(str(x) + " is een int")
		return("int")
	elif isinstance(x, float):
		#print(str(x) + " is een  float")
		return("float")
	else:
		#print(x + " is een string of character")
		return("string")

		
		
		
#global HTML_DICTIONARY
#HTML_DICTIONARY = {'\&lt;':'<', '\&gt;':'>', '\&nbsp;':' ' }
# Only replace those that are not filtered out by above UNWANTED and MEDIA_CAT functions (mostly single character)
#HTML_DICTIONARY = { '&nbsp;':' ', '&amp;':'&' }
def replace_html_codes(text, html_dic):
	for i, j in html_dic.iteritems():
		text = text.replace(i, j)
	return text
		
def calc_lat_lon(full_coords, lat_coords, lon_coords, separator):
	#latitude, longitude = calc_lat_lon(coor_list,"","", separator)
	if LANGUAGE_CODE == "nl":
		if (str(full_coords[0]) != "" and str(full_coords[4]) != ""):
			if str(full_coords[1]) == "":
				full_coords[1] = "0"
			if str(full_coords[2]) == "":
				full_coords[2] = "0"
			if str(full_coords[5]) == "":
				full_coords[5] = "0"
			if str(full_coords[6]) == "":
				full_coords[6] = "0"
			latitude = float(full_coords[0]) + ( ( float(full_coords[2])/float(60) + float(full_coords[1]))/float(60) )
			if full_coords[3] == 'S':
				latitude = -(latitude)
				longitude = float(full_coords[4]) + ((float(full_coords[6])/float(60) + float(full_coords[5]))/float(60))
				if full_coords[7] == 'W':
					longitude = -(longitude)
					#print('latitude ' + str(latitude) + ' longitude ' + str(longitude) + ' coor_string ' + coor_string)
				else:
					print('empty coordinates')
					empty_coordinates = 1
	elif LANGUAGE_CODE == "de":
		print('lat: ' + str(lat_coords[0]) + ' lon: ' + str(lon_coords))
####		