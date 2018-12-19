# -*- coding: utf-8 -*-
import numpy as np
import keras
import gensim
import sklearn.metrics
import pandas

import json
import os
import sys
import random
import collections

from learning.utils import striphtml, split_train_validation_data, f1_score, offset_binary_accuracy
from learning import config

def log(*text):
  if config.verbose:
    print(*text)

class UnknownModelException(Exception):
    pass

class Doc2vecModel(object):
    def __init__(self, model=None, deterministic=False):
        self.model = None
        self.deterministic = deterministic
        if model is not None:
            self.load_model(model)

    def load_model(self, model):
        self.model = gensim.models.Doc2Vec.load(model)
        return self

    def save_model(self, model):
        self.model.save(model)
        return self

    def train(self, data, c_data=None, epochs=10, vector_size=300, alpha=0.025):
        def to_labeled_sentence(data, c_data):
            for i, x in enumerate(data):
                if c_data:
                    yield gensim.models.doc2vec.LabeledSentence(x, [i] + c_data[i])
                else:
                    yield gensim.models.doc2vec.LabeledSentence(x, [i])
        self.model = gensim.models.Doc2Vec(vector_size=vector_size,
                                           alpha=alpha,
                                           min_alpha=alpha,
                                           min_count=1,
                                           dm=1)
        self.model.build_vocab(to_labeled_sentence(data, c_data))
        for epoch in range(epochs):
            self.model.train(to_labeled_sentence(data, c_data),
                             total_examples=self.model.corpus_count,
                             epochs=self.model.iter)
            # decrease the learning rate
            self.model.alpha -= 0.002
            # fix the learning rate, no decay
            self.model.min_alpha = self.model.alpha
        return self

    def infer_vector(self, words, seed=0):
        if self.deterministic:
            self.model.random.seed(seed) # Make the results deterministic for each prediction (obs: not over several runs)
        return self.model.infer_vector(words)

    def vector_size(self):
        if self.model:
            return self.model.vector_size
        return None

class Categorizer(object):
    def __init__(self, model_name=None, deterministic=False):
        if deterministic:
            random.seed(0)
        self.doc2vec = Doc2vecModel(config.model['path'] + '/' + config.model['doc2vec_model'], deterministic=deterministic)
        if model_name is not None:
            self.model = self.load_model(config.model['path'] + '/' + model_name)
            self.categories = self.load_model_json(config.model['path'] + '/' + model_name)['categories']
            # log("Loaded model with %s categories" % ",".join(self.categories))
        else:
            self.model = None
        self.timestep = 20
        self.n_layers = 6
        self.epochs = 15

    def preprocess_text(self, texts):
        text_words = [keras.preprocessing.text.text_to_word_sequence(striphtml(text))[1:]
                      for text in texts]
        timestep_words = [[self.doc2vec.infer_vector(seq[i*self.timestep:(i+1)*self.timestep])
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
      input_shape = (self.timestep, self.doc2vec.vector_size())
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
      #if len(sys.argv) > 1:
      #  model.load_weights(sys.argv[1])
      model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy', f1_score])
      log("Labels: ", self.categories)
      model.fit([x_train], [y_train], validation_data=([x_val], [y_val]),
                 **{'epochs': self.epochs, **model_args})
      return model

    def evaluate_categorizer(self, x_data, y_data):
        if not self.model:
            raise Exception("No model defined do evaluate")
        self.model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy', f1_score])
        y_data = [[self.categories.index(c) for c in y] for y in y_data]
        y_data_one_hot = np.array(encode_n_hot_vectors(y_data, self.categories))
        x_data_processed = np.array(self.preprocess_text(x_data))
        evaluation = self.model.evaluate([x_data_processed], [y_data_one_hot])
        log({name: val for name, val in zip(self.model.metrics_names, evaluation)})

        # Predict all values of validation data
        prediction = self.model.predict([x_data_processed])
        true_positives = len([x
                               for index, x in enumerate(prediction)
                               if x.argmax() in [i for i, y in enumerate(y_data_one_hot[index]) if y == 1.0]])
        total_predictions = len(prediction)
        log("Accuracy %f" % (true_positives / total_predictions,))

        # Compute confusion matrix of validation data
        true_values = [self.categories[y.argmax()] for y in y_data_one_hot]
        predicted_values = [self.categories[y.argmax()] for y in np.array(prediction)]
        conf_mat = sklearn.metrics.confusion_matrix(true_values, predicted_values)
        log(pandas.DataFrame(conf_mat, columns=self.categories, index=self.categories))

    def load_model_json(self, model_path):
        f = open(model_path + '.json', 'r', encoding='utf-8')
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
        self.doc2vec.save_model(os.path.dirname(path) + '/' + config.model['doc2vec_model'])


def encode_n_hot_vectors(y_data, categories=None):
    categories = categories or list(set(c for y in y_data for c in y))
    y_data_one_hot = np.zeros((len(y_data), len(categories)))
    for i, y in enumerate(y_data_one_hot):
        if 1 not in y:
            y[y_data[i]] = 1
    return y_data_one_hot


def filter_articles(data, categories):
    available_category_counts = collections.Counter([cat for x, y in data for cat in y if cat in categories])
    print(available_category_counts)
    min_category_count = available_category_counts.most_common()[-1][1]
    current_category_counts = {cat: 0 for cat in categories}
    for x, y in data:
        x = x.strip()
        if x == '':
            continue
        y = [c for c in y if c in categories]
        if not y:
            continue
        for cat in y:
            current_category_counts[cat] += 1
            if current_category_counts[cat] > min_category_count:
              break
        else:
            yield x, y

def filter_articles_category_quantity(data, threshold):
    data = list(data)
    categories = [c for x, y in data for c in y]
    quantity = collections.Counter(categories)
    for x, y in data:
        y = [c for c in y if quantity[c] >= threshold]
        if not y:
            continue
        yield x, y

def filter_article_quantity_of_categories(data, max_articles):
    available_category_counts = collections.Counter([cat for x, y in data for cat in y])
    print(available_category_counts)
    min_category_count = available_category_counts.most_common()[-1][1]
    current_category_counts = {cat: 0 for cat in available_category_counts.keys()}
    for x, y in data:
        x = x.strip()
        if x == '':
          continue
        y = [c for c in y if current_category_counts[c] < max_articles]
        if not y:
            continue
        for cat in y:
            current_category_counts[cat] += 1
        yield x, y


def filter_article_category_locations(data):
    location_json = json.load(open('learning/data/municipality_mmarea_map.json', 'r'))
    location_strings = [m['municipality'] for m in location_json] + [a['name'] for m in location_json for a in m['areas']]
    all_categories = set([category for text, categories in articles for category in categories])
    non_location_categories = [category for category in all_categories if category not in location_strings]
    return filter_articles(data, non_location_categories)


def replace_entities(data):
  import polyglot.text
  from polyglot.downloader import downloader
  downloader.download('embeddings2.sv')
  downloader.download('ner2.sv')
  for x in data:
    wrapped_text = polyglot.text.Text(x, hint_language_code='sv')
    # To filter away all words except entities use these lines
    # yield ' '.join([e for ent in text.entities for e in ent])
    # continue
    entity_idx = [i for ent in wrapped_text.entities for i in range(ent.start, ent.end)]
    words = np.array(list(wrapped_text.words))
    words[entity_idx] = [ent.tag for ent in wrapped_text.entities for i in range(ent.start, ent.end)]
    x = ' '.join(words)
    yield x

def train_and_store_model(input_file, output_file, new_doc2vec=False):
    data = json.load(open(config.data['path'] + input_file, 'r', encoding='utf-8'))['articles']
    articles = [(a['text'], a['categories']) for a in data]

    if config.data.get('target_categories', False):
        categories = open(config.data['path']+ config.data['target_categories'], 'r', encoding='utf-8').read().split('\n')
        articles = list(filter_articles(articles, categories))
    # articles = filter_article_category_locations(articles)
    articles = list(filter_article_quantity_of_categories(articles, 2000))
    articles = list(filter_articles_category_quantity(articles, 1))

    random.shuffle(articles)
    validation_split = int(0.2 * len(articles))
    x_val_data, y_val_data = zip(*articles[:validation_split])
    x_data, y_data = zip(*articles[validation_split:])
    log("Numer of articles:", len(x_data))

    if config.model['categorization_params']['use_ner']:
      x_data = list(replace_entities(x_data))
      nr_replaced_orgs = sum([text.count('ORGANISATION') for text in x_data])
      nr_replaced_locs = sum([text.count('LOCATION') for text in x_data])
      nr_replaced_pers = sum([text.count('PERSON') for text in x_data])
      nr_replaced_entities = nr_replaced_orgs + nr_replaced_locs + nr_replaced_pers
      log("Number of replaced entities:", nr_replaced_entities)
      log("  Persons:      ", nr_replaced_pers)
      log("  Organizations:", nr_replaced_pers)
      log("  Locations:    ", nr_replaced_pers)

    log("Train model")
    ## Train model ##
    if new_doc2vec:
        doc2vec = Doc2vecModel()
        doc2vec.train(x_data, y_data)
        doc2vec_file = config.get_full_model('doc2vec_model')
        doc2vec.save_model(doc2vec_file)

    callbacks = []
    if config.model['model_checkpoint']:
        checkpoint = keras.callbacks.ModelCheckpoint(config.get_full_model('model_checkpoint'),
                                                     monitor='val_loss', mode='min',
                                                     save_best_only=True, save_weights_only=True, period=5)
        tensorboard = keras.callbacks.TensorBoard(log_dir=config.model['path'] + '/Graph', histogram_freq=0, write_graph=True, write_images=True)
        callbacks = [checkpoint, tensorboard]
    categorizer = Categorizer(deterministic=False)
    model = categorizer.train_categorizer(x_data, y_data, callbacks=callbacks)
    categorizer.save_model(config.model['path'] + '/' + output_file)

    log("Evaluate model")
    ## Evaluate model ##
    categorizer = Categorizer(output_file, output_file)
    categorizer.evaluate_categorizer(x_val_data, y_val_data)

if __name__ == '__main__':
    train_and_store_model(config.data['articles'], config.model['categorization_model'], new_doc2vec=False)
