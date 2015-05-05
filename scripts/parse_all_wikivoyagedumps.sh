#!/bin/bash

# bash file to import all downloaded wikivoyage wikidumps
# version 0.2, Harry van der Wolf, 20150505

#languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 
# There are only a limited number of wikivoyage dumps available
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

