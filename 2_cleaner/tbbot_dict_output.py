
import csv 
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')

responseDictionary = dict()

with open('data.csv', mode = 'r') as infile: 
    reader = csv.reader(infile)
    next(reader, None) # skip header 
    for rows in reader: 
        if rows[5] == '': 
            continue
        else: 
            responseDictionary[rows[6]] = rows[5]

print 'Total len of dictionary', len(responseDictionary)

print 'Saving conversation data dictionary'
np.save('conversationDictionary.npy', responseDictionary)

with open('conversationData.txt', 'w') as conversationFile: 
    for key,value in responseDictionary.iteritems():
        if (not value.strip()) or value.strip == '':
            continue
        conversationFile.write(value.strip() + '\n \n')