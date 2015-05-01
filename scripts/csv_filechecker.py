#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script checks whether the created csv is correct or contains erroneous records
# version 0.1, 2015-05-01, Harry van der Wolf

import csv, sys, os
reload(sys)  
sys.setdefaultencoding('utf8')

if len(sys.argv) > 1:
	csv_file = str(sys.argv[1])
	# Check if the file exists
	if not os.path.exists(csv_file):
		print("\n\nERROR:\n   The "+ csv_file + "\" does not exist!\n\n")
		sys.exit()
else:
	print('No parameter given. You need to give the csv file name.')
	sys.exit()

correct_rows = 0
wrong_rows = 0
filename = csv_file
with open(filename, 'rb') as f:
    reader = csv.reader(f)
    try:
        for row in reader:
            correct_rows+=1
    except csv.Error as e:
        #sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
		print('file %s, line %d: %s' % (filename, reader.line_num, e))
		wrong_rows+=1
		
print('File: '+csv_file+' ; Correct rows: '+str(correct_rows)+' ; Wrong rows: '+str(wrong_rows)+' ; total lines: ' + str(reader.line_num)+'.')