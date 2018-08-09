import json
import numpy as np
import keras
import gensim
import os
import random

class UnknownModelException(Exception):
    pass

class Categorizer(object):
  def __init__(self, model_path, model_name=None, deterministic=False):
    if deterministic:
      random.seed(0)
    self.deterministic = deterministic
    self.doc2vec = gensim.models.Doc2Vec.load(model_path + '/doc2vec.model')
    if model_name is not None:
      self.model = self.load_model(model_path + '/' + model_name)
      self.categories = self.load_model_json(model_path + '/' + model_name)['categories']
      print("Loaded model with %s categories" % ",".join(self.categories))
    else:
        self.model = None
    self.timestep = 20
    self.n_layers = 4

  def infer_vector(self, words, seed=0):
    if self.deterministic:
      self.doc2vec.random.seed(seed) # Make the results deterministic for each prediction (obs: not over several runs)
    return self.doc2vec.infer_vector(words)

  def preprocess_text(self, texts):
    text_words = [keras.preprocessing.text.text_to_word_sequence(text)[1:]
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
      proba = self.model.predict([processed_text])[0]
      return {
        c: float(p)
        for c, p in zip(self.categories, list(proba))
      }

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

  def train_categorizer(self, x_data, y_data, split_train_val=0.8):
    self.categories = list(set(y_data))
    y_data = [self.categories.index(y) for y in y_data]
    y_data_one_hot = encode_one_hot_vectors(y_data)
    x_data_processed = self.preprocess_text(x_data)
    x_train, y_train, x_val, y_val = split_train_validation_data(split_train_val, x_data_processed, y_data_one_hot)

    model = self.construct_model(self.categories)
    model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy'])
    model.fit([x_train], [y_train], epochs=15, validation_data=([x_val], [y_val]))
    return model

  def evaluate_categorizer(self, x_data, y_data):
    if not self.model: raise Exception("No model defined do evaluate")
    self.model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])
    y_data = [self.categories.index(y) for y in y_data]
    y_data_one_hot = encode_one_hot_vectors(y_data, self.categories)
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


def encode_one_hot_vectors(y_data, categories=None):
  categories = categories or list(set(y_data))
  y_data_one_hot = np.zeros((len(y_data), len(categories)))
  y_data_one_hot[np.arange(len(y_data)), np.array(y_data)] = 1
  return y_data_one_hot


def filter_articles(data, categories):
  for x, y in data:
    if y not in categories:
      continue
    yield x, y



if __name__ == '__main__':
  data = json.load(open('model/data/articles.json', 'r'))['articles']
  articles = [(a['text'], a['top_category']) for a in data]
  categories = ['Sport', 'Nöje', 'Blåljus', 'Näringsliv']
  random.shuffle(articles)
  # articles = filter_articles(articles, categories)
  x_data, y_data = zip(*articles)

  ## Train model ##
  model_path = 'model/trained-models/'
  categorizer = Categorizer(model_path)
  model = categorizer.train_categorizer(x_data, y_data)
  categorizer.save_model(model_path + '/lstm-categorizer.model')

  ## Evaluate model ##
  model_path = 'model/trained-models/'
  categorizer = Categorizer(model_path, 'lstm-categorizer.model')
  categorizer.evaluate_categorizer(x_data[-10000:], y_data[-10000:])
