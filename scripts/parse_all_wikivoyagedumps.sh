#!/bin/bash

# bash file to import all downloaded wikivoyage wikidumps
# version 0.2, Harry van der Wolf, 20150505

# All 100.000+ article languages
languages="ar bg ca cs da de el en eo es et eu fa fi fr gl he hi hr hu hy id it ja kk ko la lt ms nl nn no pl pt ro ru sh simple sk sl sr sv te tr uk uz vi vo zh"
# There are only a limited number of wikivoyage dumps available (as of 13 Dec 2014)
languages="de el en es fa fr he it nl pl pt ro ru sv uk vi zh" 

for language in $languages
do
	printf "Parsing wikivoyage dump for language $language and saving csv in folder output\n\n"
	python ../scripts/parse_wikidump.py wikivoyage $language
	printf "\n\n"
done

cd ../output
# remove 0 byte files
find -name '*.csv' -size 0 -delete

