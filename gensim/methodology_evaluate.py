import sys
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', filename='tmp.log', level=logging.CRITICAL)

import gensim_documents
from PyTeaser.pyteaser import Summarize
import 	doc2vec_classify_by_decissiontree as dt, \
		doc2vec_classify_by_neuralnetwork as nn, \
		doc2vec_classify_by_randomforest as rf, \
		doc2vec_cluster_by_kmeans as km

from sklearn.model_selection import train_test_split

import ast
import numpy as np

import dotenv
dotenv.load()

resultFile = open('../Results/classify_result_2.3_vary_params_documents.pjson', 'w')

with open(dotenv.get('ARTICLE_PATH') + '/categories.pjson') as pjsonFile:
	categories = ast.literal_eval(unicode(pjsonFile.read()))

def addArticlesToVecDict(vecDict, data, documents_per_category=None, defaultCategories=None):
	global categories
	count = {}
	for article in data:
		# print article.category 
		try:
			articleCategories = ast.literal_eval(unicode(article.category))
		except Exception:
			# To handle single and multi categorised articles we add this fail safe if condition
			articleCategories = ast.literal_eval(unicode([[{'name': article.category}]]))
		# To handle single and multi categorised articles we add this fail safe if condition
		if isinstance(articleCategories, str) or isinstance(articleCategories, unicode):
			articleCategories = [[{'name': articleCategories}]]
		for categorySet in articleCategories:
			for category in categorySet:
				try:
					article.category = category['name'].encode('utf8')
				except:
					article.category = category['name']
				if defaultCategories != None and article.category not in defaultCategories:
					continue
				article_category_found = article.category in count
				if article_category_found and documents_per_category != None and count[article.category] > documents_per_category:
					continue
				if documents_per_category == None or (article.category in categories and documents_per_category <= categories[article.category]):
					#article.content = ' '.join(Summarize(article.title, "".join(article.content)))
					#article.content = gensim_documents.manipulateArticle(article.content)
					if vecDict == None or vecDict.addToDictionary(article):
						if article_category_found:
							count[article.category] += 1
						else:
							# print article.category
							count[article.category] = 1
				break
			break
	#print "BBB", unicode(count)
	return count.keys()

def dgensim(dictionary, devDict, modelPath, models):
	global resultFile
	dictionary.setModel(dotenv.get('TRAINED_SOURCES_PATH', './') + 'doc2vec_MM_14000a_' + modelPath + '_allc.model')
	devDict.setModel(dotenv.get('TRAINED_SOURCES_PATH', './') + 'doc2vec_MM_14000a_' + modelPath + '_allc.model')
	X_train, X_test, Y_train, Y_test = \
	        train_test_split(dictionary.X, dictionary.Y, test_size=.4, random_state=None)

	info = {
		'doc2vec': modelPath,
		'category_count': len(dictionary.labels),
		'document_count': len(dictionary.X),
		'dev_document_count': len(devDict.X),
		'train_size': len(X_train),
		'test_size': len(X_test),
		'min_document_length': len(dictionary.rawData[0].content.split()),
		'max_document_length': len(dictionary.rawData[-1].content.split())
	}
	for idx, model in enumerate(models):
		info['classifier'] = str(model)
		classifier = model.getClassifier()
		params = model.getAlgorithmParameters()
		paramValueMapping = [ [0, param, [val for val in values]] for idx, (param, values) in enumerate(params.iteritems()) ]
		totalNumModels = len([value for param, values in params.iteritems() for value in values])
		numModels = 0
		while sum([v[0] for v in paramValueMapping]) > 0 or numModels == 0:
			paramValueSet = {}
			for paramValue in paramValueMapping:
				paramValueSet[paramValue[1]] = paramValue[2][paramValue[0]]
			clf = model.train(X_train, Y_train, classifier(**paramValueSet))
			info['params'] = paramValueSet
			info['score'] = model.score(clf, X_test, Y_test)
			info['dev_score'] = model.score(clf, devDict.X, devDict.Y)
			# Y_pred = clf.predict(X_test)
			# from sklearn.metrics import confusion_matrix
			# print confusion_matrix(Y_test, Y_pred)
			print info
			resultFile.write(str(info) + '\n')
			numModels += 1
			# if numModels >= totalNumModels: break
			for paramValue in paramValueMapping:
				paramValue[0] += 1
				if paramValue[0] < len(paramValue[2]): break
				# if paramValue[1] == paramValueMapping[-1]: exit()
				paramValue[0] = 0
				

if __name__ == '__main__' and len(sys.argv) > 1:

	models = [dt, rf, nn]
	max_documents = 10000
	# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_mars_31_2237-filter-uuid', useHeading=True)
	# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=30000)
	data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category_uuid-filter/', useHeading=True)
	defaultCategories = addArticlesToVecDict(vecDict=None, data=data, documents_per_category=max_documents)
	devData = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_april_14_1723-filter-uuid', useHeading=True)
	if sys.argv[1] == '--length':
		devDict = gensim_documents.VectorDictionary()
		addArticlesToVecDict(devDict, data=devData,defaultCategories=defaultCategories)
		dictionary = gensim_documents.VectorDictionary()
		addArticlesToVecDict( \
			vecDict=dictionary, \
			data=data, \
			documents_per_category=max_documents, \
			defaultCategories=defaultCategories)
		X = [i[0] for i in sorted(zip(dictionary.X, dictionary.rawData), key=lambda dictEl: len(dictEl[1].content.split()))]
		Y = [i[0] for i in sorted(zip(dictionary.Y, dictionary.rawData), key=lambda dictEl: len(dictEl[1].content.split()))]
		dictionary.rawData.sort(key=lambda data: len(data.content.split()))
		rawData = dictionary.rawData
		document_length_groups = 10
		documentCount = len(dictionary.X) / document_length_groups
		for i in range(document_length_groups):
			dictionary.X = X[i*documentCount:(i+1)*documentCount]
			dictionary.Y = Y[i*documentCount:(i+1)*documentCount]
			dictionary.rawData = rawData[i*documentCount:(i+1)*documentCount]
			dgensim(dictionary, devDict, 'original', models)

	if sys.argv[1] == '--matrix':
		for category_count in [30]: #range(10, 30, 5):
			for fix_count in [max_documents]: # range(max_documents, 1000, -2000):
				## Collect the data to be trained and tested on ##
				data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category_uuid-filter/', useHeading=True, limit=fix_count)
				devDict = gensim_documents.VectorDictionary()
				addArticlesToVecDict(devDict, data=devData,defaultCategories=defaultCategories[:category_count])
				dictionary = gensim_documents.VectorDictionary()
				addArticlesToVecDict( \
					vecDict=dictionary, \
					data=data, \
					documents_per_category=fix_count, \
					defaultCategories=defaultCategories[:category_count])
				dictionary.rawData.sort(key=lambda data: len(data.content.split()))
				for linear in ['', '_linear']:
					for modelPath in ['original', 'summary', 'special', 'taggs']:
						dgensim(dictionary, devDict, modelPath + linear, models)