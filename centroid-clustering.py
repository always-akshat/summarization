__author__ = 'akshat'

import nltk
import string
import os
import numpy
import time
import redis
import logging
import math
import operator
import re
from HTMLParser import HTMLParser

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()


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


def get_members_POStagged(file_path):

    members_file = open(file_path, 'r')
    text = members_file.read().splitlines()
    members = []

    for line in text:
        t_list = members.append(string.strip(line))  #convert each line to list

    return members

def text_to_dict(file_path):
    token_dict = {}
    article_data = open(file_path, 'r')
    text = article_data.read().splitlines()

    for line in text:
        t_list = list(line.split(','))  #convert each line to list
        try:
            score = float(t_list[3])
            if score == 0:
                score = math.log(50000)
            if isinstance(score, float):
                token_dict[t_list[0]] = score
        except:
            pass

    return dict(token_dict)

clusterpath = '/home/akshat/data/hindu/plain_text/tagged/clusters'

clusters = ['cluster69']

for cluster in clusters:
    centroid_path = clusterpath + '/' + cluster + '/' + 'centroid.txt'
    centroid_dict = text_to_dict(centroid_path)
    print centroid_dict
    members_path = clusterpath + '/' + cluster + '/' + 'members.txt'
    members = get_members_POStagged(members_path)
    print members
    member_no = 0
    data = []
    for member in members:
        member_dict = text_to_dict(member)
        plaintext_path = re.sub('tagged/', '', member)
        article = open(plaintext_path, 'r')
        text = article.read().lower()
        no_tags = strip_tags(text)
        sentence_tokenize_list = sent_tokenize(no_tags)
        sentence_count = len(sentence_tokenize_list)
        print 'sentence length', sentence_count
        sentence_no = 0

        for sentence in sentence_tokenize_list:
            s_data  = {}
            #data = {'importance' :0 }
            s_data['importance'] = 0
            s_data['text'] = sentence
            s_data['sentence_no'] = sentence_no
            s_data['member_no'] = member_no
            sentence_words = word_tokenize(sentence)
            for word in sentence_words:
                if word in centroid_dict:
                    s_data['importance'] += float(centroid_dict[word])
            data.append(s_data)
            sentence_no += 1
        member_no += 1
    print data

    newlist = sorted(data, key=lambda k: k['importance'], reverse=True)[:10]

    for sentence in newlist:
        print sentence['text']
        print '**-------------------**'