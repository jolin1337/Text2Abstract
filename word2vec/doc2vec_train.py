#!/bin/bash
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim
import bz2
import tensorflowCluster as clusterAlgs

from os import listdir
from os.path import isfile, join

from pyteaser import Summarize

from numpy import dot, sqrt
from doc2vec_documents import manipulateArticle, Article, LabeledLineSentence, WikiCorpusDocuments, MMDBDocuments

def ldaLsiModeling():
    # load id->word mapping (the dictionary), one of the results of step 2 above
    id2word = gensim.corpora.Dictionary.load_from_text(bz2.BZ2File('wiki_sv_wordids.txt.bz2'))
    # load corpus iterator
    mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_sv_tfidf.mm.bz2')) # use this if you compressed the TFIDF output (recommended)
    # mm = gensim.corpora.MmCorpus('wiki_sv_tfidf.mm') # Use this for uncomressed TFIDF output

    #print(mm)

    # - LSI training
    # extract 400 LSI topics; use the default one-pass algorithm (takes roughly 4 hours)
    #lsi = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=400) #, chunksize=1, distributed=True)
    #lsi.save("wiki_sv_lsi")
    lsi = gensim.models.lsimodel.LsiModel.load('wiki_sv_lsi')
    #lsi.print_topics(10)

    # - LDA training
    #lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=1, chunksize=10000, passes=1)
    #lda.save("wiki_sv_lda")
    #lda.print_topics(10)
    lda = gensim.models.ldamodel.LdaModel.load('wiki_sv_lda')


    # - Similarity query
    doc = "dator interaktion design"
    dictionary = id2word
    vec_bow = dictionary.doc2bow(doc.lower().split())
    vec_lsi = lsi[vec_bow] # convert the query to LSI space
    #print(sorted(vec_lsi, key=lambda item: -item[1]))
    #index = gensim.similarities.MatrixSimilarity(lsi[mm], num_features=400) # transform corpus to LSI space and index it
    #index.save('wiki_sv.index')
    index = gensim.similarities.MatrixSimilarity.load('wiki_sv.index')
    index.num_best = 4
    sims = index[vec_lsi]
    #sims = sorted(enumerate(sims), key=lambda item: -item[1])
    print(sims)

    # - Trainingtime for lsi
    # test start: 2016-07-06 22:52:01,675
    # test stop:  2016-07-07 17:02:20,598



def loadTxtData(folder):

    docLabels = []
    docLabels = [f for f in listdir(folder) if f.endswith('.txt')]
    data = []
    for doc in docLabels:
        data.append(LabeledLineSentence(folder + "/" + doc))
    return data

def loadWikiData(fileName):
    pass

def traindoc2vec(sentence, model_filename='doc2vec.model'):
    model = gensim.models.Doc2Vec(alpha=0.025, min_alpha=0.025) # use fixed learning rate
    model.build_vocab(sentence)

    for epoch in range(10):
        model.train(sentence)
        model.alpha -= 0.002 # decrease the learning rate
        model.min_alpha = model.alpha # fix the learning rate, no deca
    model.save(model_filename)
    return model
def doc2vecModeling(limit=5000):
    # Three different methods of loading the data comment one out to use the other
    # data = loadTxtData("doc2vec-sources")
    #data = WikiCorpusDocuments(bz2.BZ2File('../svwiki-latest-pages-articles.xml.bz2'), limit)
    data = MMDBDocuments('/home/admin16/Documents/MM/articles_EkonomiSport.csv', useLabeldTraining=True)
    

    # Load or train the model of doc2vec 
    # additional params: size=300, window=10, min_count=5, workers=11,
    model = gensim.models.Doc2Vec.load('../doc2vec_wiki.model')
    #model = traindoc2vec(data)

    prevTitle = ""
    prevArtikel = ""
    maxSim = -1
    #fout = open('o.tmp', 'w')
    for (article, manipulatedArticle) in data: 
        if len(article.content) < 100:
            continue
        summaries = Summarize(article.title, "".join(article.content))

        wordCount = 0
        for summary in summaries:
            wordCount = wordCount + len(summary.split())
            #fout.write(summary.encode('UTF-8'))
        print "Words in original article: ", len(article.content)
        #print "Words in summary: ", wordCount
        #fout.write("\n- - - - -\n")
        if prevArtikel != "":
            sim = model.docvecs.similarity_unseen_docs(model, manipulatedArticle, prevArtikel)
            #vecA = model.infer_vector(doc_words=manipulatedArticle)
            #vecB = model.infer_vector(doc_words=prevArtikel)
            #tmp = gensim.matutils.unitvec(vecA) - gensim.matutils.unitvec(vecB)
            #sim = sqrt(dot(tmp.T, tmp))
            
            print "Article similarities: "
            print article.title.encode('UTF-8') + " <=> " + prevTitle.encode('UTF-8') + " gives a similarity of %s" % sim
            if sim > 1.0:
                print article.content.encode('UTF-8')
            #fout.write("%s" % sim)
            #fout.write("\n")
            if sim > maxSim:
                maxSim = sim
            if sim < 0.0:
                #fout.write(prevTitle.encode('UTF-8'))
                #fout.write(prevArtikel.encode('UTF-8'))
                #fout.write("\nStart___----\n")
                #fout.write(article.title.encode('UTF-8'))
                #fout.write(article.content.encode('UTF-8'))
                #fout.write("----__End")
                #fout.write("\nStart___----\n")
                #fout.write(prevTitle.encode('UTF-8'))
                #fout.write(prevArtikel.encode('UTF-8'))
                #fout.write("----__End")
                print article.title, ",", prevTitle, "=> ", sim
                #break
                pass

        prevTitle = article.title
        prevArtikel = manipulatedArticle


if __name__ == '__main__':
    data = MMDBDocuments('/home/admin16/Documents/MM/articles_EkonomiSport.csv', limit=10000, useLabeldTraining=True)
    traindoc2vec(data, model_filename='doc2vec_MM.model')