
import csv 
import numpy as np

responseDictionary = dict()

with open('data.csv', mode = 'r') as infile: 
    reader = csv.reader(infile)
    for rows in reader: 
        if (rows[1] == '' or rows[6] == ''):
            continue
        else: 
            responseDictionary[rows[6]] = rows[1]

print 'Total len of dictionary', len(responseDictionary)

print 'Saving conversation data dictionary'
np.save('conversationDictionary.npy', responseDictionary)

with open('conversationData.txt', 'w') as conversationFile: 
    for key,value in responseDictionary.iteritems():
        if (not value.strip()):
            # If there are empty strings
            continue
        conversationFile.write(value.strip() + ' ')

