#!/bin/bash
# -*- coding: utf-8 -*-

import doc2vec_clustering as classifier

import gensim_documents
from sklearn import tree, metrics
from sklearn.model_selection import train_test_split
import numpy as np
import gensim

import random

import dotenv
dotenv.load()


def getCategoryFromFile(fileName):
	return fileName.split('_MM_')[1].split('.')[0]

def train(x_train, y_train, clf = tree.DecisionTreeClassifier(criterion="entropy")):
	return clf.fit(x_train, y_train)

def score(model, x, y):
	pred = model.predict(x)
	return metrics.f1_score(y, pred, average='micro')

def getClassifier():
	return tree.DecisionTreeClassifier
def getAlgorithmParameters():
	return {
		'criterion': ['gini', 'entropy'],
		'max_features': [i * 0.1 for i in range(2, 11, 2)] + ['auto', 'sqrt', 'log2'],
		'max_depth': range(10, 50, 10),
		'min_samples_split': [i * 0.1 for i in range(2, 9, 2)],
		'min_samples_leaf': [i * 0.1 for i in range(2, 5, 2)]
	}

def pairTraining(samples=200):
	# data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/')
	data = [
		gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Allmänt.csv', limit=samples),
		gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Blåljus.csv', limit=samples),
		gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Ekonomi.csv', limit=samples),
		gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Kultur.csv', limit=samples),
		# gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Nöje.csv', limit=samples),
		# gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Släkt o vänner.csv', limit=samples),
		# gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/articles_MM_Sport.csv', limit=samples)
	]

	clfs = []
	X_tests = []
	Y_tests = []
	for mmCategory1 in data:
		for mmCategory2 in data:
			if mmCategory1.corpus == mmCategory2.corpus:
				continue
			X = []
			Y = []
			dictionary = gensim_documents.VectorDictionary()
			print "Comparing: ", getCategoryFromFile(mmCategory1.corpus), " with ", getCategoryFromFile(mmCategory2.corpus)
			for (article, _) in mmCategory1:
				dictionary.addToDictionary(article)
			c1lenx = len(dictionary.X)
			c1leny = len(dictionary.Y)
			# print getCategoryFromFile(mmCategory1.corpus), " has (x=", c1lenx, ", y=", c1leny, ") st articles"
			for (article, _) in mmCategory2:
				dictionary.addToDictionary(article)
			# print getCategoryFromFile(mmCategory2.corpus), " has (x=", len(X) - c1lenx, ", y=", len(Y) - c1leny, ") st articles"

			X_train, X_test, Y_train, Y_test = \
				train_test_split(dictionary.X, dictionary.Y, test_size=.3, random_state=42)

			X_tests = X_tests + X_test
			Y_tests = Y_tests + Y_test
			clf = train(X_train, Y_train)
			# print "Gives an accuracy score of: ", clf.score(X_test, Y_test)
			# print ""
			clfs.append(clf)

	correct = 0
	for index, _ in enumerate(X_tests):
		articlesScore = {}
		for cfl in clfs:
			# artvec = model.infer_vector(article.content)
			artvec = X_tests[index]
			predictedCategory = clf.predict([artvec])[0]
			predictedIndex = np.where(clf.classes_ == predictedCategory)
			score = clf.predict_proba([artvec])[0]
			score = score / np.sum(score)
			# print score[predictedIndex]
			if score[predictedIndex] < 0.6: #1 - 1 / len(score):
				if not predictedCategory in articlesScore:
					articlesScore[predictedCategory] = 0
				continue
			if predictedCategory in articlesScore:
				articlesScore[predictedCategory] += 1
			else:
				articlesScore[predictedCategory] = 1
		if Y_tests[index] == max(articlesScore.iterkeys(), key=lambda k: articlesScore[k]):
			correct += 1
	print correct, len(X_tests), ( 1.0 * correct ) / len(X_tests)

if __name__ == '__main__':
	pairTraining()
	# import pydotplus 
	# dot_data = tree.export_graphviz(clf, out_file=None) 
	# graph = pydotplus.graph_from_dot_data(dot_data) 
	# graph.write_pdf("iris.pdf")