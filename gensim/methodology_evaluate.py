
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', filename='tmp.log', level=logging.CRITICAL)

import gensim_documents
from PyTeaser.pyteaser import Summarize
import doc2vec_classify_by_decissiontree as dt
import doc2vec_classify_by_neuralnetwork as nn
import doc2vec_classify_by_randomforest as rf
import doc2vec_cluster_by_kmeans as km
from sklearn.model_selection import train_test_split
import dotenv
dotenv.load()
if __name__ == '__main__':
	modelPaths = ['original', 'summary', 'special', 'taggs']
	models = [nn]
	modelsConfig = [None, None, None, None] # model used for each element in the model variable
	for i in range(2):
		linear = ''
		if i == 0:
			linear = '_linear'
		for modelPath in modelPaths:
			data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=80000)
			# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=30000)
			# data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=2000)
			dictionary = gensim_documents.VectorDictionary(model=dotenv.get('TRAINED_SOURCES_PATH', './') + 'doc2vec_MM_14000a_' + modelPath + linear + '_allc.model')

			for article in data:
				article.content = ' '.join(Summarize(article.title, "".join(article.content)))
				#article.content = gensim_documents.manipulateArticle(article.content)
				dictionary.addToDictionary(article)
			print "Doc2vec model: ", modelPath
			print "Category count=", len(dictionary.labels)
			X_train, X_test, Y_train, Y_test = \
			        train_test_split(dictionary.X, dictionary.Y, test_size=.4, random_state=42)
			print "Train size = ", len(X_train)
			print "Test size = ", len(X_test)
			for idx, model in enumerate(models):
				print "Classifier: ", model
				if modelsConfig[idx] == None:
					clf = model.train(X_train, Y_train)
				else:
					clf = model.train(X_train, Y_train, model=modelsConfig[idx])

				Y_pred = clf.predict(X_test)
				print "Score = ", clf.score(X_test, Y_test)
				from sklearn.metrics import confusion_matrix
				# Printing None values of the prediction result
				# print "aa", [(i, type(i)) for i in Y_pred if i == None]
				# print "bb", (Y_pred == None)
				print confusion_matrix(Y_test, Y_pred)
