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

logging.basicConfig(filename='error.log', level=logging.ERROR)

#from collections import Counter
#from nltk.corpus import stopwords
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

start_time = time.time()
redis = redis.StrictRedis(host='xxxxx', port=xxx, db=xx)
articles_dir = '/home/akshat/data/hindu/plain_text/tagged'
clusterpath = articles_dir + '/clusters_keep_20'

similarity_dict ={}


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


    article_dict_size = 100 if len(token_dict) > 35 else len(token_dict)
    token_dict = sorted(token_dict.items(), key = lambda x :x[1], reverse = True)[:article_dict_size]
    return dict(token_dict)


def vectorize(term_dictionary):
    vectorizer = DictVectorizer(sparse=False)
    final_vector = vectorizer.fit_transform(term_dictionary)
    return final_vector


def cosine_sim(u, v):
    return numpy.dot(u, v) / (math.sqrt(numpy.dot(u, u)) * math.sqrt(numpy.dot(v, v)))


def compatible_array(from_dict, to_dict):
    from_minus_to = set(from_dict.keys()) - set(to_dict.keys())
    updated_to = dict(to_dict, **dict.fromkeys(from_minus_to, 0))
    return updated_to


def text_to_dict_with_freq(file_path):
    token_dict = {}
    article_data = open(file_path, 'r')
    text = article_data.read().splitlines()

    for line in text:
        t_list = list(line.split(','))  #convert each line to list
        try:
            data ={}
            score = float(t_list[3])
            if score == 0:
                data['score'] = math.log(50000)
            if isinstance(score, float):
                data['score'] = score

            try:
                data['freq'] = t_list[5]
            except IndexError:
                data['freq'] = 1

            token_dict[t_list[0]] = data

        except:
            pass

    return token_dict


def update_cluster(meta_file,members_path, article_dict):

    top_terms ={}
    cluster_dict = text_to_dict_with_freq(meta_file)
    lookup_writer = file(meta_file, 'w')
    for key, value in cluster_dict.iteritems():
        data ={}
        if key in article_dict:
            score = (float(value['score']) * int(value['freq']) + float(article_dict[key]))/(int(value['freq']) + 1)
            updated_tuple = str(key), 'X', 'X', score, 'X', (int(value['freq']) + 1)
            data['score'] = score
            data['freq'] = int(value['freq']) + 1
            top_terms[key] = data
        else:
            new_tuple = key, 'X', 'X', value['score'], 'X', value['freq']
            data['score'] = value['score']
            data['freq'] = value['freq']
            top_terms[key] = data

    for key, value in article_dict.iteritems():
        if key not in top_terms:
            new_tuple = key, 'X', 'X', value, 'X', 1
            data['score'] = value
            data['freq'] = 1
            top_terms[key] = data

    top_terms = sorted(top_terms.items(), key = lambda x :x[1]['score'], reverse = True)
    cluster_size = 20 if len(top_terms) > 20 else len(top_terms)

    for num in range(0, cluster_size):
        new_tuple = string.strip(top_terms[num][0]), 'X', 'X', float(top_terms[num][1]['score']), 'X', string.strip(str(top_terms[num][1]['freq']))
        lookup_writer.write('%s, %s, %s, %s, %s, %s' % new_tuple)
        lookup_writer.write('\n')



articles = [f for f in os.listdir(articles_dir) if os.path.isfile(os.path.join(articles_dir, f))]



total_processed =0

for article in articles:
    articlepath = articles_dir + '/' + article
    print articlepath
    article_dict = text_to_dict(articlepath)

    try:
        dirs = [d for d in os.listdir(clusterpath) if os.path.isdir(os.path.join(clusterpath, d))]
        print dirs
    except:
        if not os.path.exists(clusterpath): os.makedirs(clusterpath)
        dirs = []
        print 'directory created'

    if len(dirs) == 0:
        try:
                new_cluster_path = clusterpath +'/cluster1'
                new_meta_file = new_cluster_path +'/centroid.txt'
                new_lookup_file = new_cluster_path +'/members.txt'

                os.makedirs(new_cluster_path)
                lookup_writer = file(new_lookup_file, 'w')
                lookup_writer.write('%s' % articlepath)
                lookup_writer.write('\n')
                lookup_writer.close()

                with open(articlepath) as f:
                    with open(new_meta_file, "w") as f1:
                        for line in f:
                            line_list = list(line.split(','))
                            line_list[1] = 'X'
                            line_list[4] = 'X'
                            line_list.append(1)
                            f1.write('%s, %s, %s, %s, %s, %s' % tuple(line_list))
                            f1.write('\n')

        except:
            print 'something is not right'
            pass
    else:
        for cluster in dirs:
            try:

                meta_file = clusterpath +'/' + cluster +'/centroid.txt'
                cluster_dict = text_to_dict(meta_file)
                updated_cluster_dict = compatible_array(article_dict, cluster_dict)   #from,#to
                updated_article_dict = compatible_array(cluster_dict, article_dict)   #from,#to
                article_vector = vectorize(updated_article_dict)
                cluster_vector = vectorize(updated_cluster_dict)
                cos = cosine_similarity(article_vector, cluster_vector)
                similarity_dict[cluster] = cos[0][0]

            except Exception, e:
                print str(e)
                print 'maa chud gayi kahin to'
                pass

        max_sim = max(similarity_dict.iteritems(), key=operator.itemgetter(1))[0]


        if similarity_dict[max_sim] >= 0.1:
            print 'adding to the cluster' + str(max_sim)
            updated_cluster_path = clusterpath + '/' + max_sim
            updated_lookup_file = updated_cluster_path + '/members.txt'
            meta_file = updated_cluster_path + '/centroid.txt'
            lookup_writer = file(updated_lookup_file, 'a')
            lookup_writer.write('%s' % articlepath)
            lookup_writer.write('\n')
            lookup_writer.close()
            update_cluster(meta_file, updated_lookup_file, article_dict)

        else:
            print ' no use of adding. making new cluster'
            new_cluster_path = clusterpath + '/cluster' + str((len(dirs) + 1))
            new_meta_file = new_cluster_path + '/centroid.txt'
            new_lookup_file = new_cluster_path + '/members.txt'
            os.makedirs(new_cluster_path)
            lookup_writer = file(new_lookup_file, 'w')
            lookup_writer.write('%s' % articlepath)
            lookup_writer.write('\n')
            lookup_writer.close()

            with open(articlepath) as f:
                with open(new_meta_file, "w") as f1:
                    for line in f:
                        line_list = list(line.split(','))
                        line_list[1] ='X'
                        line_list[4] ='X'
                        line_list.append(1)
                        f1.write('%s, %s, %s, %s, %s, %s' % tuple(line_list))
                        f1.write('\n')

    total_processed += 1
    print total_processed
