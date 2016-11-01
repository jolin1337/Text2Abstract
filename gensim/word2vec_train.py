#!/bin/bash
# -*- coding: utf-8 -*-

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

