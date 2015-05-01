This repository holds a set of python and shell scripts to download and parse wikipedia and wikivoyage dumps from dumps.wikimedia.org

Wikipedia and wikivoyage are created by language, not by country. As such they are classified by the ISO-639-1 2-digit language code.
Wikipedia gets more and more articles where geographic coordinates are added (when applicable). Wikivoyage is a spin-off of wikipedia where it only deals about “places of interest / places to go”. Unfortunately not all articles have coordinates.

SQLite is used as cross-platform, super simple database.

It all starts with the <language_code>wiki-latest-externallinks.sql.gz dumps.
The externallinks is a huge sql script containing all links for all pages for that specific language.
Some of those inserts are “geohack” (2,3) inserts statements containing the geographic coordinates of the articles. We need those coordinates and only those links are imported and the coordinates, which we need for our articles, are extracted.  
These externallinks import will be the reference table for the sqlite database for the wikiepdia and wikivoyage articles.


Order of actions:
  - download, parse and import the <language_code>wiki-latest-externallinks.sql.gz  files into a <language_code> sqlite DB.
  - download wikipedia or wikivoyage database dumps.
  - parse wikipedia or wikivoyage dumps and import "coordiantes containing" articles into sqlite DB, based on externallinks table.
  - export imported articles with coordinates to CSV files.
  - (optionally but in this case:) Import CSV files into MapFactor Navigator Free POI mcda files (This last part not in tis repo).
