__author__ = 'akshat'

import nltk
import string
import os
import time
import redis
import logging
import math

logging.basicConfig(filename='error.log', level=logging.ERROR)

#from collections import Counter
#from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.porter import PorterStemmer

start_time = time.time()
redis = redis.StrictRedis(host='xxxx', port='xxx', db='x')
path = '/home/akshat/data/hindu/plain_text'
token_dict = {}
article_count = 0
stemmer = PorterStemmer()


def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def get_tokens(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

for subdir, dirs, files in os.walk(path):
    for file in files:
        file_path = subdir + os.path.sep + file        #subdir = /home/akshat/data, os.sep ='/'
        fileName, fileExtension = os.path.splitext(file)
        if fileExtension == '.txt' and article_count < 50000:
            club = open(file_path, 'r')
            text = club.read()
            lowers = text.lower()
            no_punctuation = lowers.translate(None, string.punctuation)
            token_dict[file] = no_punctuation
            article_count += 1
            #print 'file processed', file_path
            #print 'total time', (time.time() - start_time), 'total articles', article_count




tfidf = CountVectorizer(tokenizer=get_tokens, stop_words='english')
tfs = tfidf.fit_transform(token_dict.values())


#redis_pipe = redis.pipeline()

freq_hash = {}
idf_hash = {}
feature_names = tfidf.get_feature_names()


for col in tfs.nonzero()[1]:
    if feature_names[col] in freq_hash:
        freq_hash[feature_names[col]] += 1
    else:
        freq_hash[feature_names[col]] = 1


print len(freq_hash)
print 'article count', article_count

for k in freq_hash:
    idf_hash[k] = math.log(article_count/(freq_hash[k]))
    redis.hset('tfidf', k, idf_hash[k])


print idf_hash

print 'done'
