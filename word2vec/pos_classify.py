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
	evaluateDataCount = 2000
	trainDataCount = 2000
	data = MMDBDocuments(dotenv.get('ARTICLE_PATH') + '/articles_EkonomiSport.csv')
	nounAndVerbTags = ['NN', 'VB']
	data_iterator = iter(data)
	categories = []
	confusionMat = []
	articleDatabase = readArticleDatabase(num_sent = evaluateDataCount+trainDataCount, categories = ['Sport', 'Ekonomi'], taggs=nounAndVerbTags)
	articlesEval = []
	articlesTrain = []
	
	# Fetch all articles
	for i, (category, article) in enumerate(articleDatabase):
		if i < evaluateDataCount:
			articlesEval.append((category, article))
		else:
			articlesTrain.append((category, article))


	for i, (articleCategory, article) in enumerate(articlesEval):
		results = categoriseArticle(title='', article=' '.join(article), convergense=evaluateDataCount, db=articlesTrain)
		if len(results['scores']) == 0:
			print "Article not classified: " + i
			continue

		# Make sure that all categories are added before calculate the correct and incorrect category
		for category in results['categories']:
			if not category in categories:
				categories.append(category)
				for i, row in enumerate(confusionMat):
					confusionMat[i].append(0)
				confusionMat.append([0 for c in categories])

		categoryIndex = results['scores'].index(numpy.max(results['scores']))
		idx = categories.index(results['categories'][categoryIndex])
		cidx = categories.index(articleCategory.lower())
		confusionMat[cidx][idx] += 1
		
		print articleCategory, results['categories'][categoryIndex]

		print '\t'.join(categories)
		for index, row in enumerate(confusionMat):
			print '\t'.join([str(num) for num in row]), '\t', categories[index]

def categoriseArticle(title, article, convergense=1000, categoriesToConsider=['Sport', 'Ekonomi'], db=None):
	# This is the model to compare word similarities with
	# model = gensim.models.word2vec.Word2Vec.load(dotenv.get('WORD2VEC_MODEL'))
	model = gensim.models.doc2vec.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
	nounAndVerbTags1 = ['NOUN', 'VERB']
	nounAndVerbTags2 = ['NN', 'VB']
	article = article.split(".") #Summarize(title, article) # [art.replace(".", " ") for art in Summarize(title, article)]
	articlePos = posextractor.posSentences(article)
	if articlePos is None:
		return {}
	if db is None:
		db = readArticleDatabase(num_sent = convergense, categories = categoriesToConsider, taggs=nounAndVerbTags2)
	categoryNames = []
	categoryScores = []
	for category, nounsAndVerbs in db:
		if len(nounsAndVerbs) == 0:
			continue
		for sentenceObj in articlePos:
			articleSentenceWords = [obj.word for obj in sentenceObj if obj.tagg in nounAndVerbTags1]
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
				print "same - =)"
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

	# print categoryNames,len(articlePos), convergense
	# print [score / (len(articlePos) * convergense) for score in categoryScores]
	return {
		"categories": categoryNames,
		"scores": [score / convergense for score in categoryScores]
	}

def readArticleDatabase(num_sent, categories=[], folder='../MM/', taggs=['NN', 'VB']):
	articlesPOSFiles = [f for f in listdir(folder) if f.endswith('.conll')]
	for articlesOfCategoryFileName in articlesPOSFiles:
		category = [category for category in categories if category in articlesOfCategoryFileName]
		if len(category) == 0:
			continue
		category = category[0]

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
	

	#articleDatabase = readArticleDatabase(num_sent = 10, categories = ['Sport', 'Ekonomi'], taggs=['NN', 'VB'])
	# for c, i in articleDatabase:
	# 	print c, i
	# 	break
	# for j in articleDatabase:
	# 	print c, i
	# 	break
