#!/bin/bash

# bash file to import all downloaded wikivoyage wikidumps
# version 0.1, Harry van der Wolf, 20150428

# Run from the scripts folder

languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 

mkdir -p ../output
for language in $languages
do
# we can't nest the combined sqlite command nicely, so "un"nest everything and let it start at first postion on the line
printf " Exporting wikivoyagedump to csv for language $language\n\n"
sqlite3 ../sqlite/${language}wikipedia.db <<!
.headers on
.mode csv
.output ../output/${language}wikivoyage.csv
select * from ${language}_wikivoyage;
!
# do some reformating like the &lt; to < and &gt; to >
printf "Some additional cleaning of the csv files"
sed -e 's+&amp;+&+g' -e 's+&gt;+>+g' -e 's+&lt;+<+g' -e 's+nbsp;+ +g' ${language}wikivoyage.csv > ${language}wikivoyage2.csv
mv ${language}wikivoyage2.csv ${language}wikivoyage.csv

printf "\n\n"
done
