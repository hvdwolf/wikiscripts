#!/bin/bash

# bash file to download and parse one or multiple external links dumps
# version 0.3, Harry van der Wolf, 20150505

for i in "${@}"
do
  printf "Downloading language $i\n\n"
  wget -c http://dumps.wikimedia.org/${i}wiki/latest/${i}wiki-latest-externallinks.sql.gz
  printf "Done downloading $i."
  python3 ../scripts/externallinks.py $i
  rm ${i}wiki-latest-externallinks.sql.gz
done
