# coding: utf-8

x_data = []
y_data = []
from random import shuffle
import gensim_documents

data = gensim_documents.MMDBDocumentLists('../MM/csv_by_category/', useHeading=True, limit=5000)
articles = [(a.content, a.category) for a in data if a.category != 'Allmänt']
shuffle(articles)
categories = list(set(list(zip(*articles))[1]))
train_test_split = int(len(articles) * 0.8)
articles_train = [(a[0], categories.index(a[1])) for a in articles]
articles_test = [(a[0], categories.index(a[1])) for a in articles[train_test_split:]]
'''
rootdir = 'D:/Topic/code/segment/data/lstm_train/7_Confuse/shuffle'
articles_train_text = open(rootdir + '/train.txt','r',encoding='utf-8').read().split('\n')
articles_train_label = open(rootdir + '/train_label2.txt','r',encoding='utf-8').read().split('\n')
articles_test_text = open(rootdir + '/test.txt','r',encoding='utf-8').read().split('\n')
articles_test_label = open(rootdir + '/test_label2.txt','r',encoding='utf-8').read().split('\n')
articles_train = list(zip(articles_train_text, articles_train_label))
articles_test = list(zip(articles_test_text, articles_test_label))
categories = set(articles_train_label)
'''

wordVectorLength = 250
docVectorLength = 100
import gensim
import numpy as np
import keras
# Load word2vec model
w2v_model = gensim.models.Word2Vec.load('../gensim/trained-sources/word2vec_MM_180521.model')
#d2v_model = gensim.models.Doc2Vec.load('doc2vec.model')

articles_train_labels, articles_train_vectors = zip(*[
    (int(label),
      [w2v_model.wv[word] for word in text.split(' ') if word in w2v_model.wv]
    ) for text, label in articles_train
])
# articles_train_labels, articles_train_vectors = zip(*[
#     (int(label), [[w2v_model.wv[word]
#       for word in sentence.split(' ') if word in w2v_model.wv]
#       for sentence in sentences.split('。')])
#       for sentences, label in articles_train

# ])
#print(articles_train_vectors[0])

articles_test_labels, articles_test_vectors = zip(*[
    (int(label), [w2v_model.wv[word]
      for word in text.split(' ') if word in w2v_model.wv])
      for text, label in articles_test
])
# articles_test_labels, articles_test_vectors = zip(*[
#     (int(label), [[w2v_model.wv[word]
#       for word in sentence.split(' ') if word in w2v_model.wv]
#       for sentence in sentences.split('。')])
#       for sentences, label in articles_test

# ])

article_length = 80
articles_train_vectors = [[article[i] if len(article) > i else np.zeros(len(articles_train_vectors[0][0])) for i in range(article_length)] for article in articles_train_vectors]
articles_test_vectors = [[article[i] if len(article) > i else np.zeros(len(articles_test_vectors[0][0])) for i in range(article_length)] for article in articles_test_vectors]

y_data_one_hot = np.zeros((len(articles_train_vectors), len(categories)))
y_data_one_hot[np.arange(len(articles_train_labels)), np.array(articles_train_labels)] = 1

x_data = np.array(articles_train_vectors)

y_test_one_hot = np.zeros((len(articles_test_vectors),len(categories)))
y_test_one_hot[np.arange(len(articles_test_labels)), np.array(articles_test_labels)] = 1

x_test = np.array(articles_test_vectors)

print(np.array(x_data).shape)
data_dim = len(x_data[0][0])
timesteps = len(x_data[0])

num_classes = len(categories)



split = 0.2
limit_train = (int)(len(x_data) * split)
# Generate dummy training data
x_train = x_data[:limit_train]
y_train = y_data_one_hot[:limit_train]

# Generate dummy validation data
x_val = x_data[limit_train:]
y_val = y_data_one_hot[limit_train:]


from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Embedding
from keras.layers import LSTM,Bidirectional
import numpy as np
from keras.layers.core import Activation, Reshape
from keras.layers import Conv1D, MaxPooling1D,ConvLSTM2D,BatchNormalization


print('data_dim=' ,data_dim)
print('timesteps=' , timesteps)
input_shape = (timesteps, data_dim,)
print(input_shape, np.array(x_train).shape)

model = Sequential()

model.add(Bidirectional(LSTM(50, return_sequences=True,dropout=0.5),
               input_shape=input_shape))
model.add(Conv1D(64,
             7,
             padding='valid',
             activation='relu',
             strides=1
             #input_shape = ( timesteps, data_dim )
             ))
model.add(MaxPooling1D(pool_size=4))

model.add(Dropout(0.2))


model.add(Flatten())

model.add(Dense(num_classes, activation='softmax'))


model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])
model.fit(x_train, y_train, epochs=5, validation_data=(x_val, y_val))


from sklearn.metrics import confusion_matrix

prediction = model.predict(x_val)
conf_mat = confusion_matrix([categories[y.argmax()] for y in y_val], [categories[y.argmax()] for y in np.array(prediction)])
print(categories)
print(conf_mat)
model_name = "./trained-sources/CNN-category-model"
# serialize model to JSON
model_json = model.to_json()
with open(model_name + '.json', 'w') as json_file:
    json_file.write(model_json)
# serialize weights to HDF5
model.save_weights(model_name + '.h5')
print("Saved model to disk as", model_name)
'''
#10-crossvalidation
n_folds = 10
labels = to_categorical(np.asarray(articles_train_label))
c, r = labels.shape
labels = y_data.reshape(c,)
skf = StratifiedKFold(labels, n_folds=n_folds, shuffle=True)
from keras.utils import to_categorical
from keras.layers import Conv1D, MaxPooling1D
from sklearn.cross_validation import StratifiedKFold
for i, (train, test) in enumerate(skf):
    print ("Running Fold", i+1, "/", n_folds)
    model = Sequential()
    model.add(Bidirectional(LSTM(50, return_sequences=True,dropout=0.5),
                   input_shape=(timesteps, data_dim)))
    model.add(Conv1D(64,
                 5,
                 padding='valid',
                 activation='relu',
                 strides=1
                 #input_shape = ( timesteps, data_dim )
                 ))
    model.add(MaxPooling1D(pool_size=4))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(num_classes, activation='softmax'))
    model.compile(loss='categorical_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])
    # print('train='+ data[train])
    # print('lable='+ labels[train])

    labels1 = to_categorical(labels[train])
    labels2 = to_categorical(labels[test])
    model.fit(data[train], labels1, epochs=1, batch_size=128)
    print(model.evaluate(data[test], labels2))
'''
#10-

#print(model.evaluate(x_test, y_test))
