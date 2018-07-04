#!/bin/bash
# -*- coding: utf-8 -*-
'''
from gensim_documents import manipulateArticle, Article, LabeledLineSentence, WikiCorpusDocuments, MMDBDocuments


from PyTeaser.pyteaser import Summarize
import posextractor
import gensim
import os
import dotenv
dotenv.load()

class LabeledSentenceDocument(object):
  def __init__(self, dirname, categories=[]):
    self.dirname = dirname
    self.categories = categories
  def __iter__(self):
    print "Start processing word2vec train"
    conllFiles = [file for file in os.listdir(self.dirname) if file.endswith(".conll")]
    print conllFiles
    for i, conllFile in enumerate(conllFiles):
      if len([True for cat in self.categories if conllFile.find(cat) > -1]) > 0:
        print "Processing " + " file " + str(i) + ": " + conllFile
        poses = posextractor.readPOSFromConll(self.dirname + conllFile)
        for posSentence in poses:
          toYield = [manipulateArticle(tagg.word) for tagg in posSentence if tagg.tagg in ["VB", "NN"]]
          #print toYield
          if len(toYield) > 0:
            yield toYield
          #yield gensim.models.doc2vec.LabeledSentence(words=toYield, taggs=["TAGG %s" % i])
    print "Finnished processing word2vec train"
    return
    #docs = MMDBDocuments(self.file, limit=1000)
    for doc, mandoc in docs:
      sumDoc = Summarize(doc.title, doc.content)
      for sumDocInstance in sumDoc:
        for sumDocInstance in sumDocInstance.split("."):
          sumDoc = posextractor.posSentence(manipulateArticle(sumDocInstance))
          for taggs in sumDoc:
            toYield = [tagg.word for tagg in taggs if tagg.tagg in ["VB", "NN"]]
            print toYield
            yield toYield

if __name__ == '__main__':
  sentences = LabeledSentenceDocument(dotenv.get('ARTICLE_PATH', './'), ['Sport', 'Ekonomi'])
  #sents = [sent.encode('utf-8').split() for sent in ['testar nu bara', 'korridora under bordet']]
  model = gensim.models.word2vec.Word2Vec(sentences)
  model.save(dotenv.get('WORD2VEC_MODEL'))
  print "Saved word2vec model: " + dotenv.get('WORD2VEC_MODEL')
  model = gensim.models.word2vec.Word2Vec.load(dotenv.get('WORD2VEC_MODEL'))
'''




from gensim.models import word2vec
import gensim.parsing.preprocessing as preprocessing
import logging

import gensim_documents
import random

def process(doc):
  CUSTOM_FILTERS = [
    preprocessing.strip_tags,
    preprocessing.split_alphanum,
    preprocessing.strip_non_alphanum,
    preprocessing.strip_multiple_whitespaces,
    lambda d: d.lower(),
    lambda d: d.replace('!', '.'),
    lambda d: d.replace('?', '.')
  ]
  #print(' '.join(preprocessing.preprocess_string(doc, CUSTOM_FILTERS)))
  return ' '.join(preprocessing.preprocess_string(doc, CUSTOM_FILTERS))

def main():
  logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
  data = gensim_documents.MMDBDocumentLists('../MM/csv_by_category/', useHeading=True, limit=-1)
  docs = [s.split()  for a in data for s in process(a.content).split('.')]
  random.shuffle(docs)
  model = word2vec.Word2Vec(docs, window=6, size=250)
  model.save(u"../gensim/trained-sources/word2vec_MM_180521.model")

  #class gensim.models.word2vec.Word2Vec(sentences=None, size=100, alpha=0.025, window=5, min_count=5, max_vocab_size=None, sample=0.001, seed=1, workers=3, min_alpha=0.0001, sg=0, hs=0, negative=5, cbow_mean=1, hashfxn=<built-in function hash>, iter=5, null_word=0, trim_rule=None, sorted_vocab=1, batch_words=10000)


  # how to load a model ?
  # model = word2vec.Word2Vec.load_word2vec_format("your_model.bin", binary=True)

if __name__ == '__main__':
  main()
  model = word2vec.Word2Vec.load("trained-sources/word2vec_MM_180521.model")
  #print(model.wv['sundsvall'])
  #print(model.wv.most_similar('kommunfullmäktige'))
  print()
  print(model.wv.most_similar(positive=['kommunfullmäktige'], negative=['försämringar']))
  #print(model.wv.closer_than('tennis', 'fotboll'))
  #print(model.wv.closer_than('skola', 'busshållplats'))
