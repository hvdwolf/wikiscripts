#!/bin/bash

# bash file to download and parse all available external links dumps
# version 0.2, Harry van der Wolf, 20150505

printf "Downloading language $1\n\n"
wget -c http://dumps.wikimedia.org/${1}wiki/latest/${1}wiki-latest-externallinks.sql.gz
printf "Done downloading $1."
python ../scripts/externallinks.py $1
rm ${1}wiki-latest-externallinks.sql.gz
done
