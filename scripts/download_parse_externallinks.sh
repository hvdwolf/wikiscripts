#!/bin/bash

# bash file to download and parse all available external links dumps
# version 0.1, Harry van der Wolf, 20150426

printf "Downloading language $1\n\n"
python ../scripts/wikiextlinksdownloader.py $1
printf "Done downloading $1."
python ../scripts/externallinks.py $1
#rm ${1}wiki-latest-externallinks.sql.gz
done
