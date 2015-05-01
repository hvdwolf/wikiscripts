#!/bin/bash

# bash file to import all downloaded wikivoyage wikidumps
# version 0.1, Harry van der Wolf, 20150428

# Run from the scripts folder

languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 

mkdir -p ../output
for language in $languages
do
# we can't nest the combines sqlite command, so "un"nest everything
printf " Exporting wikivoyagedump to csv for language $language\n\n"
sqlite3 ../sqlite/${language}wikipedia.db <<!
.headers on
.mode csv
.output ../output/${language}wikivoyage.csv
select * from ${language}_wikivoyage;
!
printf "\n\n"
done
