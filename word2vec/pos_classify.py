#!/bin/bash
# -*- coding: utf-8 -*-

#For testing
from doc2vec_documents import MMDBDocuments

# Needed libraryies
import posextractor
import doc2vec_documents as documents
import gensim
import numpy
from PyTeaser.pyteaser import Summarize
import dotenv
from os import listdir
import sys  

dotenv.load()
reload(sys)  
sys.setdefaultencoding('utf8')

def evaluate():
	evaluateDataCount = 5000
	data = MMDBDocuments(dotenv.get('ARTICLE_PATH') + '/articles_EkonomiSport.csv')
	data_iterator = iter(data)
	truePositives = 0
	falsePositives = 0
	for article, mancontent in data:
		if evaluateDataCount > 0:
			evaluateDataCount -= 1
			continue
		results = categoriseArticle(article.title, article.content, evaluateDataCount)
		if len(results['scores']) == 0:
			print "Article not classified: " + article.title
			continue

		categoryIndex = results['scores'].index(numpy.max(results['scores']))
		if results['categories'][categoryIndex] == article.category.lower():
			truePositives += 1
		else:
			falsePositives += 1
		print article.category, results['categories'][categoryIndex]
		print "True positives: ", truePositives
		print "False positives: ", falsePositives


def categoriseArticle(title, article, convergense=1000, categoriesToConsider=['Sport', 'Ekonomi']):
	# This is the model to compare word similarities with
	# model = gensim.models.word2vec.Word2Vec.load(dotenv.get('WORD2VEC_MODEL'))
	model = gensim.models.doc2vec.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
	nounAndVerdTags1 = ['NOUN', 'VERB']
	nounAndVerdTags2 = ['NN', 'VB']

	article = article.split(".") #Summarize(title, article) # [art.replace(".", " ") for art in Summarize(title, article)]
	articlePos = posextractor.posSentences(article)

	if articlePos is None:
		return {}

	article_count = 6000
	categoryNames = []
	categoryScores = []
	for category, nounsAndVerbs in readArticleDatabase(num_sent = article_count, categories = categoriesToConsider, taggs=nounAndVerdTags2):
		if len(nounsAndVerbs) == 0:
			continue
		for sentenceObj in articlePos:
			articleSentenceWords = [obj.word for obj in sentenceObj if obj.tagg in nounAndVerdTags1]
			if len(articleSentenceWords) == 0:
				continue
			#print [obj.word for obj in sentenceObj], [obj.tagg for obj in sentenceObj]
			while True:
				try:
					# Score is the similarity between these sentences (using cosine similarity 
					# score = model.n_similarity(articleSentenceWords, nounsAndVerbs)
					score = model.docvecs.similarity_unseen_docs(model, articleSentenceWords, nounsAndVerbs)
					break
				except KeyError as e:
					if e.args[0] in nounsAndVerbs:
						nounsAndVerbs.remove(e.args[0])
					elif e.args[0] in articleSentenceWords:
						# print e.args
						articleSentenceWords.remove(e.args[0])
					else:
						score = 0
						break
					# for word in nounsAndVerbs:
					# 	print str(e, 'utf-8')[1:-1].encode('utf-8'), word.encode('utf-8')
			if score >= 1.0:
				print "=("
				print articleSentenceWords, nounsAndVerbs
				# exit()
				# continue
			if category in categoryNames:
				index = categoryNames.index(category)
				categoryScores[index] += score
			else:
				categoryNames.append(category)
				categoryScores.append(score)
				# exit()

	# print categoryNames
	# print [score / (len(articlePos) * article_count) for score in categoryScores]
	return {
		"categories": categoryNames,
		"scores": [score / article_count for score in categoryScores]
	}

def readArticleDatabase(num_sent, categories=[], folder='../MM/', taggs=['NN', 'VB']):
	articlesPOSFiles = [f for f in listdir(folder) if f.endswith('.conll')]

	for articlesOfCategoryFileName in articlesPOSFiles:
		category = [category for category in categories if category in articlesOfCategoryFileName]
		if len(category) == 0:
			continue
		category = category[0]

		print articlesOfCategoryFileName

		articlesOfCategoryPOS = posextractor.readPOSFromConll(folder + articlesOfCategoryFileName, num_sent)
		words = ''
		for articleSentencePOS in articlesOfCategoryPOS:
			words = ' '.join([article.word for article in articleSentencePOS if article.tagg in taggs])
			# print '\t'.join([article.word for article in articleSentencePOS])
			# print '\t"'.join([article.tagg for article in articleSentencePOS])
			# print ' '.join([article.word for article in articleSentencePOS if article.tagg in ["VB", "NN"]])
			# print " "
			yield (category.lower(), words.split())


if __name__ == '__main__':
	evaluate()