__author__ = 'akshat'

import nltk
import string
import os
import time
import redis
import logging



start_time = time.time()
redis = redis.StrictRedis(host='xxxx', port='xxx', db='xxx')
readpath = '/home/akshat/data/de-news-v0.91/txt/vector/de-news-1999-08-10.en.txt'


with open(readpath) as f:
    content = f.read().splitlines()


for line in content:
    print line
    x =(line,)
    print list(x)
    exit()
    #for (term, score, type) in line:
        #print term, ' -- ', score
