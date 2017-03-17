import numpy as np
import gensim_documents
import doc2vec_classify_by_decissiontree as dt
import doc2vec_classify_by_neuralnetwork as nn
import doc2vec_classify_by_randomforest as rf
import doc2vec_cluster_by_kmeans as km
from sklearn.model_selection import train_test_split
import dotenv
dotenv.load()
#
# Data processing
#
data = gensim_documents.MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category/', limit=1000)
# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=77851)
# data = gensim_documents.MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv', limit=10000)

dictionary = gensim_documents.VectorDictionary()
for (article, _) in data:
	dictionary.addToDictionary(article)


X_train, X_test, Y_train, Y_test = \
        train_test_split(dictionary.X, dictionary.Y, test_size=.3, random_state=42)
#
# Training
#
dt_model = dt.train(X_train, Y_train)
nn_model = nn.train(X_train, Y_train)
rf_model = rf.train(X_train, Y_train)

#
# Testing
#
dt_pred = dt_model.predict_proba(X_test)
nn_pred = nn_model.predict_proba(X_test)
rf_pred = rf_model.predict_proba(X_test)
wisdom = [nn_model.classes_[np.argmax(dt_pred[i] * 0.2 + rf_pred[i] * 0.39 + nn_pred[i] * 0.7)] for i in range(len(dt_pred))]
correct_classified = [1 for idx, prediction in enumerate(wisdom) if prediction == Y_test[idx]]
print dt_model.classes_, nn_model.classes_
print "Wisdom-score: ", float(sum(correct_classified)) / len(wisdom)
print "DecissionTree-score: ", dt_model.score(X_test, Y_test)
print "NeuralNetwork-score: ", nn_model.score(X_test, Y_test)