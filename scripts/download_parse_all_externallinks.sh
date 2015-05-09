#!/bin/bash

# bash file to download and parse all available external links dumps
# version 0.2, Harry van der Wolf, 20150505

# All 100.000+ article languages
languages="ar bg ca cs da de el en eo es et eu fa fi fr gl he hi hr hu hy id it ja kk ko la lt ms nl nn no pl pt ro ru sh simple sk sl sr sv te tr uk uz vi vo zh"

for language in $languages
do
        printf "Downloading language $language\n\n"
	wget -c http://dumps.wikimedia.org/${language}wiki/latest/${language}wiki-latest-externallinks.sql.gz
	printf "Done downloading $language."
	python ../scripts/externallinks.py $language
	rm ${language}wiki-latest-externallinks.sql.gz
done
