#!/bin/bash

# bash file to download all available wikidumps
# version 0.1, Harry van der Wolf, 20150419

#languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nl nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 
# There are only a limited number of wikivoyage dumps available
languages="de el en es fa fr he it nl pl pt ro ru sv uk vi zh" 

for language in $languages
do
	printf "Downloading language $language\n\n"
	wget -c http://dumps.wikimedia.org/${language}wikivoyage/latest/${language}wikivoyage-latest-pages-articles.xml.bz2
done
