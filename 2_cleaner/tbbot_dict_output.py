
import csv 
import numpy as np
import codecs
from cleanMessage import cleanMessage
from punct_tokenizer import token_lookup, tokenize_regex, tokenize_utf8
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


print 'Writing raw conversation data'
with open('rawConversationData.txt', 'w') as conversationFile: 
    for key,value in responseDictionary.iteritems():
        if (not value.strip()) or value.strip == '':
            continue
        conversationFile.write(cleanMessage(value).strip() + ' <EOM> ')


print 'Writing clean conversation data'
with open('cleanConversationData.txt', 'w') as cleanFile:
    rawText = ""
    with codecs.open('rawConversationData.txt', 'r', 'utf-8') as words: 
        with codecs.open('masterBannon.txt', 'r', 'utf-8') as more_words:
            rawText += tokenize_utf8(words.read())
            rawText += tokenize_utf8(more_words.read())
            rawText = tokenize_regex(rawText)

            token_dict = token_lookup()

            for token, replacement in token_dict.items(): 
                rawText = rawText.replace(token, ' {} '.format(replacement))

            cleanFile.write(rawText)