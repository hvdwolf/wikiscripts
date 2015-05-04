#!/bin/bash

# bash file to clean csv files by contry code given
# Can be: ../scripts/clean_csv.sh nl
# or: ../scripts/clean_csv.sh nl en no sv de

# version 0.1, Harry van der Wolf, 20150504

for i in "${@}"
do
  # do some reformating like the &lt; to < and &gt; to >
  printf "Some additional cleaning of the csv files"
  sed -e 's+&amp;+&+g' -e 's+&gt;+>+g' -e 's+&lt;+<+g' -e 's+nbsp;+ +g' ${i}_wikipedia.csv > ${i}_wikipedia2.csv
  mv ${i}_wikipedia2.csv ${i}_wikipedia.csv

printf "\n\n"
done

# remove 0 byte files
find -name '*.csv' -size 0 -delete

