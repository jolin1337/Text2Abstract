import numpy as np
import keras
import gensim

import json
import os
import sys
import random
import collections

from learning.utils import striphtml

class UnknownModelException(Exception):
    pass

class Categorizer(object):
  def __init__(self, model_path, model_name=None, deterministic=False):
    if deterministic:
      random.seed(0)
    self.deterministic = deterministic
    self.doc2vec = gensim.models.Doc2Vec.load(model_path + '/doc2vec_MM.model')
    if model_name is not None:
      self.model = self.load_model(model_path + '/' + model_name)
      self.categories = self.load_model_json(model_path + '/' + model_name)['categories']
      print("Loaded model with %s categories" % ",".join(self.categories))
    else:
        self.model = None
    self.timestep = 20
    self.n_layers = 6
    self.epochs = 20

  def infer_vector(self, words, seed=0):
    if self.deterministic:
      self.doc2vec.random.seed(seed) # Make the results deterministic for each prediction (obs: not over several runs)
    return self.doc2vec.infer_vector(words)

  def preprocess_text(self, texts):
    text_words = [keras.preprocessing.text.text_to_word_sequence(striphtml(text))[1:]
                  for text in texts]
    timestep_words = [[self.infer_vector(seq[i*self.timestep:(i+1)*self.timestep], seed=0)
                       for i in range(self.timestep)]
                       for seq in text_words]
    pad_words = [seq[0:self.timestep] + [0] * max(0, self.timestep - len(seq))
                 for seq in timestep_words]
    return pad_words

  def categorize_text(self, text):
      if self.model == None:
        raise UnknownModelException()
      processed_text = self.preprocess_text(text)
      probas = self.model.predict([processed_text])
      return [{
        c: float(p)
        for c, p in zip(self.categories, list(proba))
      } for proba in probas]

  def construct_model(self, categories):
    num_classes = len(categories)
    ##### expected input data shape: (batch_size, timesteps, data_dim)
    input_shape = (self.timestep, self.doc2vec.vector_size,)
    model = keras.models.Sequential()
    model.add(keras.layers.LSTM(50,
              input_shape=input_shape,
              return_sequences=True))  # returns a sequence of vectors of dimension 50
    for layer in range(self.n_layers-2):
      model.add(keras.layers.Dropout(0.2))
      model.add(keras.layers.LSTM(50, return_sequences=True))  # returns a sequence of vectors of dimension 50
    model.add(keras.layers.LSTM(50))  # return a single vector of dimension 50
    model.add(keras.layers.Dense(num_classes, activation='softmax'))
    self.model = model
    return model

  def train_categorizer(self, x_data, y_data, split_train_val=0.8, **model_args):
    self.categories = list(set(c for y in y_data for c in y))
    y_data = [[self.categories.index(c) for c in y] for y in y_data]
    y_data_one_hot = encode_n_hot_vectors(y_data)
    x_data_processed = self.preprocess_text(x_data)
    x_train, y_train, x_val, y_val = split_train_validation_data(split_train_val, x_data_processed, y_data_one_hot)

    model = self.construct_model(self.categories)
    if len(sys.argv) > 1:
      model.load_weights(sys.argv[1])
    model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy'])
    model.fit([x_train], [y_train], validation_data=([x_val], [y_val]),
              **{epochs: self.epochs, **model_args})
    return model

  def evaluate_categorizer(self, x_data, y_data):
    if not self.model: raise Exception("No model defined do evaluate")
    self.model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    y_data = [[self.categories.index(c) for c in y] for y in y_data]
    y_data_one_hot = encode_n_hot_vectors(y_data, self.categories)
    x_data_processed = self.preprocess_text(x_data)
    evaluation = self.model.evaluate([x_data_processed], [y_data_one_hot])
    print({name: val for name, val in zip(self.model.metrics_names, evaluation)})

  def load_model_json(self, model_path):
    f = open(model_path + '.json', 'r')
    model_json_str = f.read()
    f.close()
    return json.loads(model_json_str)


  def load_model(self, model_path):
    model_json = self.load_model_json(model_path)
    model_json_str = json.dumps(model_json)
    model = keras.models.model_from_json(model_json_str)
    model.load_weights(model_path + '.h5')
    model._make_predict_function()
    return model

  def save_model(self, path):
    model_json = json.loads(self.model.to_json())
    model_json['categories'] = self.categories
    json.dump(model_json, open(path + '.json', 'w'))
    self.model.save_weights(path + '.h5')


def load_model(model_path, *vargs, **dargs):
    model_seg = model_path.split('/')
    return Categorizer(*vargs, model_path='/'.join(model_seg[:-1]), model_name=model_seg[-1], **dargs)

def split_train_validation_data(split, x_data, y_data):
  limit_train  = (int)(len(x_data) * split)
  return x_data[:limit_train], y_data[:limit_train], \
         x_data[limit_train:], y_data[limit_train:]


def encode_n_hot_vectors(y_data, categories=None):
  categories = categories or list(set(c for y in y_data for c in y))
  y_data_one_hot = np.zeros((len(y_data), len(categories)))
  for i, y in enumerate(y_data_one_hot):
    y[y_data[i]] = 1
  return y_data_one_hot


def filter_articles(data, categories):
  for x, y in data:
    y = [c for c in y if c in categories]
    if not y:
      continue
    yield x, y
  return []

def filter_articles_category_quantity(data, threshold):
  data = list(data)
  categories = [c for x, y in data for c in y]
  quantity = collections.Counter(categories)
  for x, y in data:
    y = [c for c in y if quantity[c] >= threshold]
    if not y:
      continue
    yield x, y
  return []


if __name__ == '__main__':
  data = json.load(open('learning/data/articles_all_categories.json', 'r'))['articles']
  articles = [(a['text'], a['categories']) for a in data]
  # articles = [(a['text'], [a['top_category']]) for a in data]
  top_categories = [
    'Kultur','Släkt o vänner','Ekonomi',
    'Nostalgi','Mat',
    'Nöje','Trafik','Sport',
    'Inrikes','Fritid','Resor',
    'Bostad',
    'Utrikes','Motor','Opinion',
    'Blåljus','Näringsliv',
    #'Allmänt'
  ]
  all_categories = [
    "Mat","Böcker","Innebandy","Ishockey","Minnesord","Fotboll","Sport","Blåljus","Längdskidor","Motor","Nöje","Hockeyallsvenskan","SHL","Ledare","Bandy","Utrikes","TV", "Brott","Konsument","Skidsport","Musik","Div 1","Konst","Trafik","Kultur","Släkt o vänner","Bostad","Inrikes","Nostalgi","Allsvenskan","Debatt","Bränder","Insändare","Opinion","Ekonomi","Teater","Näringsliv","Film","Olyckor","Fira o Uppmärksamma"
  ]
  categories = all_categories
  random.shuffle(articles)
  articles = filter_articles(articles, categories)
  articles = filter_articles_category_quantity(articles, 100)
  x_data, y_data = zip(*articles)

  ## Train model ##
  model_path = 'learning/trained-models/'
  checkpoint = keras.callbacks.ModelCheckpoint(model_path + 'checkpoint.weights.e{epoch:02d}-loss{val_loss:.2f}-acc{val_acc:.2f}.hdf5',
                                               monitor='val_loss', mode='min',
                                               save_best_only=True, save_weights_only=True, period=5)
  categorizer = Categorizer(model_path, deterministic=True)
  model = categorizer.train_categorizer(x_data, y_data, checkpoint=checkpoint)
  categorizer.save_model(model_path + '/lstm-multi-categorizer-larger.model')

  ## Evaluate model ##
  categorizer = Categorizer(model_path, 'lstm-multi-categorizer-larger.model')
  categorizer.evaluate_categorizer(x_data[-10000:], y_data[-10000:])
