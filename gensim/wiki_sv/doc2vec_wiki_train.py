#!/bin/bash
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import gensim
import bz2

from os import listdir
from os.path import isfile, join

class WikiCorpusDocuments(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        uid = 0
        pages = gensim.corpora.wikicorpus.extract_pages(bz2.BZ2File(self.filename))
        for title, doc, pageid in pages:
            if uid > 2000:
                break
            doc = gensim.corpora.wikicorpus.remove_markup(doc)
            unallowedChars = ["!", "*","(",")", "'", "\"", "=",":", ",", ".", ";", "-", "\n"]
            for uc in unallowedChars:
                doc = doc.replace(uc, ' ')
            uid = uid + 1
            yield gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=['SENT_%s' % pageid, title])


sentence = WikiCorpusDocuments('svwiki-latest-pages-articles.xml.bz2')
model = gensim.models.Doc2Vec(alpha=0.025, min_alpha=0.025) # use fixed learning rate
model.build_vocab(sentence)

for epoch in range(10):
    model.train(sentence)
    model.alpha -= 0.002 # decrease the learning rate
    model.min_alpha = model.alpha # fix the learning rate, no deca
model.save('doc2vec_wiki.model')