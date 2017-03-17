#!/bin/bash
# -*- coding: utf-8 -*-

import doc2vec_clustering as classifier

from PyTeaser.pyteaser import Summarize
import gensim_documents
# from sklearn.cluster import KMeans
import tensorflow_cluster as clusterAlgs
from sklearn.model_selection import train_test_split
import numpy as np
import collections
import gensim

import random

import dotenv
dotenv.load()

class kMeans(object):
	"""A method to evaluate and predict cluster objects"""
	def __init__(self):
		self.categories = []
		self.centroids = None
	def fit(self, x_train, y_train=[]):
		cat = np.unique(y_train)
		nrofclusters = len(cat)
		self.categories = [None] * nrofclusters
		(centroids, assignments) = clusterAlgs.TFKMeansCluster(x_train, noofclusters=nrofclusters, noofiterations=15, useCosineDistance=False)
		for clusterIndex in range(nrofclusters):
			clusterArticles = [y_train[idx] for idx, assignment in enumerate(assignments) if len(y_train) > idx and assignment == clusterIndex]
			comons = collections.Counter(clusterArticles).most_common(nrofclusters)
			for (category, count) in comons:
				if not category in self.categories:
					self.categories[clusterIndex] = category
					break
		#self.categories = [c if c != None else cat[i] for (c, i) in enumerate(self.categories)]
		# print self.categories, cat
		self.centroids = centroids
		return self
	def predict(self, documents):
		return [self.categories[
						np.argmax([
							np.dot(centroid / np.linalg.norm(centroid), document / np.linalg.norm(document)) 
								for centroid in self.centroids
						])
					] for document in documents]
		# return [self.categories[docIndex] for docIndex in self.clf.predict(documents)]
	def score(self, x_test, y_test):
		sum = np.sum([1 for idx, category in enumerate(self.predict(x_test)) if category == y_test[idx]])
		return float(sum) / len(y_test)


def train(x_train, labels, clf = None):
	if clf == None:
		nrofclusters = len(np.unique(labels))
		clf = kMeans()
		# clf = KMeans(n_clusters=nrofclusters, random_state=42)
	return clf.fit(x_train, labels)

if __name__ == '__main__':
	# Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
	model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
	data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=10000)

	dictionary = gensim_documents.VectorDictionary()

	for article in data:
		dictionary.addToDictionary(article)


	X_train, X_test, Y_train, Y_test = \
		train_test_split(dictionary.X, dictionary.Y, test_size=.3, random_state=42)
	clf = train(X_train, Y_train)
	nrofclusters = len(dictionary.labels)
	categories = []
	for clusterIndex in range(nrofclusters):
		clusterArticles = [dictionary.Y[idx] for idx, assignment in enumerate(clf.labels_) if assignment == clusterIndex]
		comons = collections.Counter(clusterArticles).most_common(nrofclusters)
		for category in comons:
			if not category[0] in categories:
				categories.append(category[0])
				break

	print categories[clf.predict_prob([X_test[0]])[0]], Y_test[0]
	sum = np.sum([1 for idx, clusterIndex in enumerate(clf.predict(X_test)) if categories[clusterIndex] == Y_test[idx]])
	print sum, len(dictionary.Y)
	print float(sum) / len(Y_test)