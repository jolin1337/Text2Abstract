#!/bin/bash
# -*- coding: utf-8 -*-

import doc2vec_clustering as classifier

import gensim_documents
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from sklearn.model_selection import train_test_split
import gensim

import random

import dotenv
dotenv.load()

def train(x_train, y_train, clf = MLPClassifier(alpha=0.003, solver='lbfgs', activation='logistic', max_iter=1000)):
	return clf.fit(x_train, y_train)

# def score(model, x, y):
# 	return model.score(x, y)
def score(model, x, y):
	pred = model.predict(x)
	return metrics.f1_score(y, pred, average='micro')
def getClassifier():
	return MLPClassifier
def getAlgorithmParameters():
	return {
		'hidden_layer_sizes': [[a for a in (100 for i in range(1, j, 1))] for j in range(2, 8, 1)],
		'activation': ['identity', 'logistic', 'tanh', 'relu'],
		'solver': ['lbfgs', 'sgd', 'adam'],
		'alpha': [i * 0.001 for i in range(5, 21, 5)],
		'max_iter': [1000]
	}

if __name__ == '__main__':
	modelPaths = ['original', 'special', 'summary', 'taggs']
	for modelPath in modelPaths:
		# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=77851)
		# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=30000)
		data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=77851)
		dictionary = gensim_documents.VectorDictionary(model=dotenv.get('TRAINED_SOURCES_PATH', './') + 'doc2vec_MM_14000a_' + modelPath + '_linear_allc.model')

		for article in data:
			dictionary.addToDictionary(article)
		print "Categories: ", dictionary.labels, ", count=", len(dictionary.labels)
		X_train, X_test, Y_train, Y_test = \
		        train_test_split(dictionary.X, dictionary.Y, test_size=.4, random_state=42)
		clf = train(X_train, Y_train)

		Y_pred = clf.predict(X_test)
		print "Score = ", clf.score(X_test, Y_test)
		from sklearn.metrics import confusion_matrix
		print confusion_matrix(Y_test, Y_pred)


# [
# 	[0.6687857596948507,0.08836617927527018,0.00572155117609663,0.04195804195804196,0.020343293070565798,0.0025429116338207248,0.0019071837253655435,0.11697393515575334,0,0.0050858232676414495,0.04831532104259377],
# 	[0.2388818297331639,0.6086404066073697,0,0.007623888182973317,0.0038119440914866584,0.0012706480304955528,0.0012706480304955528,0.054637865311308764,0,0.0038119440914866584,0.08005082592121983],
# 	[0.32558139534883723,0,0.5116279069767442,0,0.023255813953488372,0,0.023255813953488372,0.11627906976744186,0,0,0],
# 	[0.22258064516129034,0.041935483870967745,0,0.46774193548387094,0.03870967741935484,0.0032258064516129032,0.0064516129032258064,0.1064516129032258,0,0.0032258064516129032,0.10967741935483871],
# 	[0.1072463768115942,0.020289855072463767,0.002898550724637681,0.028985507246376812,0.41739130434782606,0,0.002898550724637681,0.39710144927536234,0,0.002898550724637681,0.020289855072463767],
# 	[0.08333333333333333,0,0,0,0.008333333333333333,0.8,0.008333333333333333,0.075,0,0.008333333333333333,0.016666666666666666],
# 	[0.11904761904761904,0,0,0.047619047619047616,0,0.023809523809523808,0.5,0.30952380952380953,0,0,0],
# 	[0.0396138482023968,0.009653794940079893,0,0.006990679094540613,0.021970705725699067,0.0019973368841544607,0.0013315579227696406,0.8119174434087882,0,0.004327563249001331,0.10219707057256991],
# 	[0,0,0,0,0.25,0,0,0.25,0,0,0.5],
# 	[0.1875,0.078125,0,0.0078125,0.015625,0.0078125,0.0078125,0.34375,0,0.1875,0.1640625],
# 	[0.026397515527950312,0.013198757763975156,0,0.005822981366459627,0.0015527950310559005,0.0007763975155279503,0.0007763975155279503,0.10830745341614907,0,0.003105590062111801,0.8400621118012422]
# ]
# [
# 	[0.67,	0.09,	0.01,	0.04,	0.02,	0,		0,		0.12,		0,		0.01,	0.05],
# 	[0.24,	0.61,	0,		0.01,	0,		0,		0,		0.05,		0,		0,		0.08],
# 	[0.33,	0,		0.51,	0,		0.02,	0,		0.02,	0.12,		0,		0,		0],
# 	[0.22,	0.04,	0,		0.47,	0.04,	0,		0.01,	0.11,		0,		0,		0.11],
# 	[0.11,	0.02,	0,		0.03,	0.42,	0,		0,		0.4,		0,		0,		0.02],
# 	[0.08,	0,		0,		0,		0.01,	0.8,	0.01,	0.08,		0,		0.01,	0.02],
# 	[0.12,	0,		0,		0.05,	0,		0.02,	0.5,	0.31,		0,		0,		0],
# 	[0.04,	0.01,	0,		0.01,	0.02,	0,		0,		0.81,		0,		0,		0.1],
# 	[0,		0,		0,		0,		0.25,	0,		0,		0.25,		0,		0,		0.5],
# 	[0.19,	0.08,	0,		0.01,	0.02,	0.01,	0.01,	0.34,		0,		0.19,	0.16],
# 	[0.03,	0.01,	0,		0.01,	0,		0,		0,		0.11,		0,		0,		0.84]
# ]


# [[0.57,0.15,0.08,0.06,0.08,0.04,0.03],
#  [0.14,0.71,0.05,0.02,0.01,0.02,0.04],
#  [0.08,0.05,0.67,0.06,0.04,0.04,0.05],
#  [0.03,0.04,0.08,0.58,0.15,0.09,0.03],
#  [0.03,0.03,0.05,0.13,0.66,0.05,0.06],
#  [0.03,0.06,0.06,0.06,0.08,0.64,0.07],
#  [0.05,0.05,0.05,0.04,0.07,0.06,0.68]]
