#!/bin/bash

# bash file to download all available wikidumps
# version 0.1, Harry van der Wolf, 20150419

languages="ar ca cs da de el en eo es et eu fa fi fr gl he hi hr hu it ja ko lt ms nn no pl pt ro ru simple sk sl sr sv te tr uk vi vo zh" 

for language in $languages
do
	printf "Downloading language $language\n\n"
	python wikimediadownloader.py $language
done