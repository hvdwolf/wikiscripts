#!/bin/bash

# bash file to import all downloaded wikivoyage wikidumps
# version 0.1, Harry van der Wolf, 20150428

#languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 
# There are only a limited number of wikivoyage dumps available
languages="de el en es fa fr he it nl pl pt ro ru sv uk vi zh" 

now="$(date +%Y%m%d-%H%M%S)"

printf "$(date +%Y%m%d-%H%M%S) ;" > $now.log 
for language in $languages
do
	printf "$(date +%Y%m%d-%H%M%S)" >> $now.log
	printf "Importing wikivoyage dump for language $language\n\n"
        printf "Importing wikivoyage dump for language $language\n\n" >> $now.log
	python ../scripts/parse_wikivoyagedump.py $language
	printf "\n\n"
	printf "\n\n" > $now.log
done

cd ../output
# remove 0 byte files
find -name 'file*' -size 0 -delete

