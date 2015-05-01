#!/bin/bash

# bash file to download and parse all available external links dumps
# version 0.1, Harry van der Wolf, 20150426

languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh"

for language in $languages
do
        printf "Downloading language $language\n\n"
        #python ../scripts/wikiextlinksdownloader.py $language
	printf "Done downloading $language."
	python ../scripts/externallinks.py $language
	rm ${language}wiki-latest-externallinks.sql.gz
done
