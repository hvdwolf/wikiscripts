#!/bin/bash

# Use wget -c for continued downloads as well
# The possible languages are listed below
# ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nn no pl pt ro ru simple sk sl sr sv
# te tr uk vi vo zh"

# Script usage
# From dumps   ../scripts/wikimediadownloader.sh nl
# to download the Dutch wikipedia pages dump
#
# or from folder dumps:  ../scripts/wikimediadownloader.sh de en fr pl
# to download the German, English, French and Polish wikipedia pages dump
#
# ALWAYS CHECK YOUR DOWNLOADED DUMP WITH SOMETHING LIKE bzip2 -t <language_code>wiki-latest-pages-articles.xml.bz2
# You do not want your pc to work for hours and then stop because your dump is corrupt. It happens with these
# Gigabit size dumps

for x in "${@}"
do
  wget -c http://dumps.wikimedia.org/${x}wiki/latest/${x}wiki-latest-pages-articles.xml.bz2
done
