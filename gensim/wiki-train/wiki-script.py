#!/bin/bash
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim
import bz2

from os import listdir
from os.path import isfile, join

#from pyteaser import Summarize


def ldaLsiModeling():
    # load id->word mapping (the dictionary), one of the results of step 2 above
    id2word = gensim.corpora.Dictionary.load_from_text(bz2.BZ2File('wiki_sv/wiki_sv_wordids.txt.bz2'))
    # load corpus iterator
    mm = gensim.corpora.MmCorpus(bz2.BZ2File('wiki_sv/wiki_sv_tfidf.mm.bz2')) # use this if you compressed the TFIDF output (recommended)
    #MmCorpus.serialize('test.mm', corpus)
    # mm = gensim.corpora.MmCorpus('wiki_sv_tfidf.mm') # Use this for uncomressed TFIDF output
    print mm

    #logent = gensim.models.LogEntropyModel(mm, id2word=id2word)
    #logent.save('wiki_sv/logent.model')
    #logent = gensim.models.LogEntropyModel.load('wiki_sv/logent.model')
    tfidf = gensim.models.TfidfModel.load('wiki_sv/wiki_sv.tfidf_model')

    # - LSI training
    # extract 400 LSI topics; use the default one-pass algorithm (takes roughly 4 hours)
    #lsi = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=400) #, chunksize=1, distributed=True)
    #lsi.save("wiki_sv_lsi")
    lsi = gensim.models.lsimodel.LsiModel.load('wiki_sv/wiki_sv_lsi')
    # lsi.print_topics(1000)
    # exit()
    # - LDA training
    #lda = gensim.models.ldamodel.LdaModel(corpus=mm, id2word=id2word, num_topics=100, update_every=1, chunksize=10000, passes=1)
    #lda.save("wiki_sv_lda")
    # lda = gensim.models.ldamodel.LdaModel.load('wiki_sv/wiki_sv_lda')
    #lda.print_topics(10)
    # index = gensim.similarities.MatrixSimilarity.load('wiki_sv/wiki_sv.index')
    # index = gensim.similarities.MatrixSimilarity(lsi[mm])
    # index.save('wiki_sv/wiki_sv_lsi.index')
    index = gensim.similarities.MatrixSimilarity.load('wiki_sv/wiki_sv_lsi.index')
    index.num_best = 100


    print "Start evaluating"
    # - Similarity query
    doc = "dator interaktion design"
    dictionary = gensim.corpora.Dictionary.load('wiki_sv/wiki_sv.dict') #id2word
    docs = 'Marie Munters från Dala-Järna, bor sedan en tid tillbaka i Brasilien, där hon jobbar som beridare i en stor ridklubb.Marie, som representerar Vansbro Ryttarsällskap, tävlar också också i Sydamerika och nyligen nådde hon fina framgångar i en dressyrtävling.Med hästen Donfire S:t George slutade Marie 1:a i Intermediate freestyle och 2:a i Intermediate.Med hästen Crossy blev det en 2:a plats i Grand Prix freestyle och en 3:e plats i Grand Prix. '
    docs = [docs]#docs.split('. ')
    corpuses = [dictionary.doc2bow(doc.lower().split()) for doc in docs]

    for corpus in corpuses:
        #index = gensim.corpus.Similarity(corpus=lsi[logent[corpus]], num_features=400, output_prefix='shard')
        sims_to_query = index[lsi[tfidf[corpus]]]
        print sims_to_query
        eq = ""
        for doc_index in sims_to_query:
            if eq != "":
                eq += " + "
            eq += "\"" + dictionary.get(doc_index[0], '::') + "\"*" + str(doc_index[1])
        print eq
        # best_score = max(sims_to_query)
        # avg_score = sum(sims_to_query) / len(sims_to_query)
        # sims_index = sims_to_query.tolist().index(best_score)
        # print avg_score, sims_index, best_score, dictionary.get(sims_index, '::')
    # vec_lsi = lsi[vec_bow] # convert the query to LSI space
    # print lsi.show_topics(vec_lsi[0])
    #print(sorted(vec_lsi, key=lambda item: -item[1]))
    #index = gensim.similarities.MatrixSimilarity(lsi[mm], num_features=400) # transform corpus to LSI space and index it
    #index.save('wiki_sv.index')
    # index.num_best = 4
    # sims = index[vec_lsi]
    #sims = sorted(enumerate(sims), key=lambda item: -item[1])
    # print(sims)

    # - Trainingtime for lsi
    # test start: 2016-07-06 22:52:01,675
    # test stop:  2016-07-07 17:02:20,598

class LabeledLineSentence(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        for uid, line in enumerate(open(self.filename)):
            yield gensim.models.doc2vec.LabeledSentence(words=line.split(), tags=['SENT_%s' % uid])
class WikiCorpusDocuments(object):
    def __init__(self, corpus):
        self.corpus = corpus
    def __iter__(self):
        uid = 0
        pages = gensim.corpora.wikicorpus.extract_pages(bz2.BZ2File('svwiki-latest-pages-articles.xml.bz2'))
        for title, doc, pageid in pages:
            if uid > 2000:
                break
            doc = gensim.corpora.wikicorpus.remove_markup(doc)
            unallowedChars = ["!", "*","(",")", "'", "\"", "=",":", ",", ".", ";", "-", "\n"]
            for uc in unallowedChars:
                doc = doc.replace(uc, ' ')
            uid = uid + 1
            yield doc.split()
            #yield gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=['SENT_%s' % pageid, title])

def loadTxtData(folder):

    docLabels = []
    docLabels = [f for f in listdir(folder) if f.endswith('.txt')]
    data = []
    for doc in docLabels:
        data.append(LabeledLineSentence(folder + "/" + doc))
    return data

def loadWikiData(fileName):
    pass

def traindoc2vec(sentence):
    model = gensim.models.Doc2Vec(alpha=0.025, min_alpha=0.025) # use fixed learning rate
    model.build_vocab(sentence)

    for epoch in range(10):
        model.train(sentence)
        model.alpha -= 0.002 # decrease the learning rate
        model.min_alpha = model.alpha # fix the learning rate, no deca
    model.save('doc2vec_wiki.model')
    return model
def doc2vecModeling():


    # data = loadTxtData("doc2vec-sources")
    #data = gensim.corpora.wikicorpus.WikiCorpus("svwiki-latest-pages-articles.xml.bz2")
    data = WikiCorpusDocuments(gensim.corpora.wikicorpus.extract_pages('svwiki-latest-pages-articles.xml.bz2'))
    #gensim.corpora.mmcorpus.MmCorpus.serialize("wiki_sv_wikicorpus.data", data)
    #data = gensim.corpora.mmcorpus.MmCorpus('wiki_sv_wikicorpus.data')
    #print data.get_texts()
    #for doc in data:
    #   print doc
    #   break
    # additional params: size=300, window=10, min_count=5, workers=11,
    model = gensim.models.Doc2Vec.load('doc2vec_wiki.model')
    #model = traindoc2vec(data)
    # it = DocIt.DocIterator(data, docLabels)
    #return
    prevArtikel = ""
    for currentArtikel in data: 
        summaries = Summarize('', currentArtikel)

        wordCount = 0
        for summary in summaries:
            print summary
            wordCount += len(summary.split())

        print "Words in original article: ", len(article.split()) + len(title.split())
        print "Words in summary: ", wordCount
        print "-----"
        if prevArtikel is "":
            prevArtikel = currentArtikel
        else:
            print model.docvecs.similarity_unseen_docs(model, currentArtikel, currentArtikel)
            break
    #print model.similarity('flicka', 'grabb')

ldaLsiModeling()