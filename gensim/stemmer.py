import nltk
from nltk.stem.snowball import SnowballStemmer
import re
from sklearn import tree
import gensim
import doc2vec_classify_by_decissiontree as doc2vec_decissiontree

import dotenv
dotenv.load()

def tokenize_and_stem(text):
	stemmer = SnowballStemmer("swedish")
	try:
		text = unicode(text, errors="ignore")
	except:
		text = text
	tokens = [word for sent in nltk.tokenize.sent_tokenize(text) 
						for word in nltk.tokenize.word_tokenize(sent) 
							if re.search('[a-zA-Z]', word)]
	stems = [stemmer.stem(t.strip()) for t in tokens]
	return stems

taggArray = []
for i, tagg in enumerate(open(dotenv.get('ARTICLE_PATH', '.') + '/taggs_new_query_2017_03_16.csv', 'r')):
	if i == 0: continue
	tagg_count = tagg.rsplit(",", 1)
	taggArray.append((tagg_count[0], 0)) #int(tagg_count[1])))
# taggArray.sort(lambda a, b: a[1] - b[1])
taggs = " ".join([tagg[0] for i, tagg in enumerate(taggArray) if i < 3000])

taggs = tokenize_and_stem(taggs[1:])

def text_to_taggs(text):
	global taggs
	return [word for word in tokenize_and_stem(text) if word in taggs]

def train(x_train, y_train, clf = tree.DecisionTreeClassifier(criterion="entropy")):
	return doc2vec_decissiontree.train(x_train, y_train, clf=clf)

if __name__ == '__main__':
	import gensim_documents
	from sklearn.neural_network import MLPClassifier
	from sklearn.model_selection import train_test_split
	import numpy as np

	import random


	# data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=30000)
	# data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=77851)
	data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=2000)
	dictionary = gensim_documents.VectorDictionary()
	for article in data:
		article.content = " ".join(text_to_taggs(article.content))
		dictionary.addToDictionary(article)


	X_train, X_test, Y_train, Y_test = \
		train_test_split(dictionary.X, dictionary.Y, test_size=.4, random_state=42)
	clf = doc2vec_decissiontree.train(X_train, Y_train)
	# clf = MLPClassifier(alpha=1, solver='lbfgs', activation='logistic', max_iter=1000)
	Y_pred = clf.predict(X_test)
	print "Score = ", clf.score(X_test, Y_test)
	from sklearn.metrics import confusion_matrix
	cm = confusion_matrix(Y_test, Y_pred)
	print cm
   	cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
   	print "Normalised: "
   	print cm
	print dictionary.labels
	# print tokenize_and_stem(taggs[1:])

# [[ 0.26405868  0.17359413  0.11369193  0.08435208  0.08557457  0.15036675	0.12836186]
 # [ 0.18159509  0.23558282  0.12760736  0.08588957  0.07607362  0.13128834	0.16196319]
 # [ 0.11636829  0.1112532   0.27621483  0.14450128  0.12404092  0.11764706	0.10997442]
 # [ 0.10858586  0.04924242  0.10732323  0.35858586  0.15277778  0.13005051	0.09343434]
 # [ 0.10383189  0.09641533  0.13102596  0.15203956  0.23238566  0.13349815	0.15080346]
 # [ 0.1182266   0.12561576  0.08990148  0.09482759  0.12807882  0.26724138	0.17610837]
 # [ 0.1373057   0.14248705  0.11139896  0.09067358  0.10362694  0.15414508	0.26036269]]