__author__ = 'akshat'

import nltk
import string
import os
import time
import redis
import logging
from HTMLParser import HTMLParser

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.tag.stanford import POSTagger
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

start_time = time.time()
stemmer = PorterStemmer()
redis = redis.StrictRedis(host='xxx', port=xx, db=x)
readpath = '/home/akshat/data/hindu/plain_text/'
writepath = readpath + 'tagged/'
print writepath




st = POSTagger(r'/home/akshat/nltk_data/stanford-postagger-2014-08-27/models/english-left3words-distsim.tagger',
                           r'/home/akshat/nltk_data/stanford-postagger-2014-08-27/stanford-postagger.jar')
print 'in the loop'
for subdir, dirs, files in os.walk(readpath):
    for file in files:
        file_path = subdir + os.path.sep + file        #subdir = /home/akshat/data, os.sep ='/'
        fileName, fileExtension = os.path.splitext(file)
        old_files =[]
        try:
            old_files = [f for f in os.listdir(writepath) if os.path.isfile(os.path.join(writepath, f))]
            if len(old_files)== 0:
                print ' 0 files found'
        except:
            if not os.path.exists(writepath): os.makedirs(writepath)
            print 'directory created'

        if not file in old_files:
            print 'file name ' + file
            writepath_file = writepath + fileName+'.txt'
            output_file = open(writepath_file, 'w')
            output_file.write('term, tf, idf, tf-idf, type\n')

            article = open(file_path, 'r')
            text = article.read().lower()
            no_tags = strip_tags(text)
            no_punctuation = no_tags.translate(None, string.punctuation)
            word_tokenize_list = tokens = nltk.word_tokenize(no_punctuation)
            word_tokenize_list = [string.strip(f) for f in word_tokenize_list]
            word_count = len(word_tokenize_list)
            print word_count

            filtered_words =[]
            word_freq ={}
            #filtered_words = [w for w in word_tokenize_list if not unicode(w) in stopwords.words('english')]
            for w in word_tokenize_list:
                if not w in stopwords.words('english'):
                    try:
                        if not w in word_freq:
                            filtered_words.append(unicode(w))
                            word_freq[w] = 1
                        else:
                            word_freq[w] += 1
                    except:
                        print 'something is wrong'
                        pass

            tagged = st.tag(filtered_words)


            for (v, t) in tagged:
                if t in ['NN', 'NNS', 'NNP', 'NNPS']:
                    idf = redis.hget('tfidf', stemmer.stem(v))
                    try:
                        idf = float(idf)
                        tf = int(word_freq[v])
                        score = tf * idf
                        term_tuple = v, tf, idf, score, t
                        output_file.write('%s, %s, %s,%s,%s' % term_tuple)
                        output_file.write('\n')
                    except:
                        pass

            print 'total time  :' + str(time.time() - start_time)
        else:
            print 'file found' + str(file)


#sent_tokenize_list = sent_tokenize(text)
#sentence_count = len(sent_tokenize_list)
#print 'sentence length', sentence_count
#print 'tokenized sentences \n', sent_tokenize_list

