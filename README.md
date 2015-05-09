This repository holds a set of python and shell scripts to download and parse wikipedia and wikivoyage dumps from dumps.wikimedia.org

NOTE: Currently the state of these scripts is under constant change.

Wikipedia and wikivoyage are created by language, not by country. As such they are classified by the ISO-639-1 2-digit language code.
Wikipedia gets more and more articles where geographic coordinates are added (when applicable). Wikivoyage is a spin-off of wikipedia where it only deals about “places of interest / places to go / what to see”, etcetera. Unfortunately not all articles have coordinates.

SQLite is used as cross-platform, super simple database to hold the "intermediate" data.

It all starts with the \<language_code\>wiki-latest-externallinks.sql.gz dumps.
The externallinks is a huge sql script containing all links for all pages for that specific language.
Some of those inserts are “geohack” insert statements containing the geographic coordinates (and title) of the articles. We need those coordinates. Only the links with those coordinates are imported, as we need the title and coordinates to match agains the articles which we extract from the dumps.  
In other words: These externallinks imports will be the reference tables for the sqlite database for the wikiepdia and wikivoyage articles.


Order of actions:
  - download, parse and import the \<language_code\>wiki-latest-externallinks.sql.gz  files into a \<language_code\>_wikipedia sqlite DB.
  - download wikipedia or wikivoyage database dumps.
  - parse wikipedia or wikivoyage dumps and create a csv and/or gpx and/or osm and/or sql file based on externallinks table (optionally import "coordinates containing" articles into sqlite DB).
  - Clean csv files before further processing.
  
The script writes (can write) csv, gpx, osm and sql output so you can use the output in multiple tools to create POI files.

The current goal (my goal) of these scripts is to convert the created CSV files into MapFactor Navigator Free POI mca files to be used in Mapfactor Navigator Free. 
This convert step and program (diggerQT/digger_console) is not part of this repository and not part of this GPL-2 license.
