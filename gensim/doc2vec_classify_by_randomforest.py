#!/bin/bash
# -*- coding: utf-8 -*-

import doc2vec_clustering as classifier

import gensim_documents
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
import gensim

import random

import dotenv
dotenv.load()

def train(x_train, y_train, clf = RandomForestClassifier(criterion="entropy",random_state=42)):
	return clf.fit(x_train, y_train)

# def score(model, x, y):
# 	return model.score(x, y)
def score(model, x, y):
	pred = model.predict(x)
	return metrics.f1_score(y, pred, average='micro')

def getClassifier():
	return RandomForestClassifier
def getAlgorithmParameters():
	return {
		'n_estimators': range(5, 26, 5),
		'criterion': ['gini', 'entropy'],
		'max_features': [i * 0.1 for i in range(2, 11, 2)] + ['auto', 'sqrt', 'log2'],
		'max_depth': range(10, 50, 10),
		'min_samples_split': [i * 0.1 for i in range(2, 9, 2)],
		'min_samples_leaf': [i * 0.1 for i in range(2, 5, 2)]
	}

if __name__ == '__main__':
	data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=77851)
	# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=77851)
	# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=30000)

	dictionary = gensim_documents.VectorDictionary()

	for (article, _) in data:
		dictionary.addToDictionary(article)
	print "Categories: ", dictionary.labels, ", count=", len(dictionary.labels)
	X_train, X_test, Y_train, Y_test = \
	        train_test_split(dictionary.X, dictionary.Y, test_size=.3, random_state=42)
	clf = train(X_train, Y_train)

	Y_pred = clf.predict(X_test)
	print "Score = ", clf.score(X_test, Y_test)
	from sklearn.metrics import confusion_matrix
	print confusion_matrix(Y_test, Y_pred)