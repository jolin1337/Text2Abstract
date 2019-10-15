# -*- coding: utf-8 -*-
import numpy as np
import keras
import sklearn.metrics

import json
import random
import collections

from learning.utils import split_train_validation_data
from learning import config
from learning.lstm_categorizer_model import LSTMCategorizer
from learning.blstm_categorizer_model import BLSTMCategorizer
from learning.doc2vec_model import Doc2vecModel
from learning.word2vec_model import Word2vecModel
from learning.logger import log


class UnknownModelException(Exception):
    pass


def filter_articles(data, categories):
    available_category_counts = collections.Counter([cat for x, y in data for cat in y if cat in categories])
    min_category_count = available_category_counts.most_common()[-1][1]
    current_category_counts = {cat: 0 for cat in categories}
    for x, y in data:
        x = x.strip()
        if x == '':
            continue
        y = [c for c in y if c in categories and current_category_counts[c] < min_category_count]
        if not y:
            continue
        for cat in y:
            current_category_counts[cat] += 1
            #if current_category_counts[cat] > min_category_count:
            #  break
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


def get_articles():
    data = json.load(open(config.data['path'] + config.data['articles'], 'r', encoding='utf-8'))['articles']
    articles = [(a['headline'] + ' ' + a['text'], a['categories']) for a in data]

    if config.data.get('target_categories', False):
        categories = open(config.data['path']+ config.data['target_categories'], 'r', encoding='utf-8').read().split('\n')
        articles = filter_articles(list(articles), categories)
    # articles = filter_article_category_locations(articles)
    articles = filter_article_quantity_of_categories(list(articles), 1862)
    articles = filter_articles_category_quantity(list(articles), 1)
    return list(articles)


def get_vector_model(x_data=None, y_data=None, **params):
    vec_model = Word2vecModel
    if config.model['vec_model']['type'] == 'doc2vec':
        vec_model = Doc2vecModel
    random.seed(0)
    vec_file = config.model['path'] + config.model['vec_model']['name']
    if config.model['vec_model']['train']:
        vec = vec_model(deterministic=params.get('deterministic', False))
        vec.train(x_data, y_data, vector_size=params.get('vector_size', None))
        vec.save_model(vec_file)
    if vec is None:
        vec = vec_model(model=vec_file,
                        deterministic=params.get('deterministic', False))
    return vec


def get_categorization_model(vec, source=None):
    if config.model['categorization_model']['type'] == 'lstm':
        return LSTMCategorizer(vec, source)
    return BLSTMCategorizer(vec, source)


def train_and_store_model(evaluate=False):
    articles = get_articles()
    random.shuffle(articles)
    log("Numer of articles:", len(articles))
    available_category_counts = collections.Counter([cat for text, categories in articles for cat in categories])
    log(available_category_counts)
    x_val_data, y_val_data, x_data, y_data = split_train_validation_data(0.1, *zip(*articles))

    if config.model['categorization_model']['use_ner']:
        x_data = list(replace_entities(x_data))
        nr_replaced_orgs = sum([text.count('ORGANISATION') for text in x_data])
        nr_replaced_locs = sum([text.count('LOCATION') for text in x_data])
        nr_replaced_pers = sum([text.count('PERSON') for text in x_data])
        nr_replaced_entities = nr_replaced_orgs + nr_replaced_locs + nr_replaced_pers
        log("Number of replaced entities:", nr_replaced_entities)
        log("  Persons:      ", nr_replaced_pers)
        log("  Organizations:", nr_replaced_pers)
        log("  Locations:    ", nr_replaced_pers)

    log("Train vec model")
    # Train model #
    vec = get_vector_model(x_data, y_data, deterministic=True)
    callbacks = []
    log("Train categorization model")
    if config.model['categorization_model']['model_checkpoint']:
        checkpoint = keras.callbacks.ModelCheckpoint(config.model['path'] + config.model['categorization_model']['model_checkpoint'],
                                                     monitor='val_loss', mode='min',
                                                     save_best_only=True, save_weights_only=True, period=5)
        tensorboard = keras.callbacks.TensorBoard(log_dir=config.model['path'] + '/Graph', histogram_freq=0, write_graph=True, write_images=True)
        callbacks = [checkpoint, tensorboard]

    categorizer = get_categorization_model(vec)
    categorizer.train_categorizer(x_data, y_data, callbacks=callbacks)
    categorizer.save_model(config.model['path'] + config.model['categorization_model']['name'])

    if evaluate:
        log("Evaluate model")
        # Evaluate model #
        categorizer = get_categorization_model(None, config.model['path'] + config.model['categorization_model']['name'])
        categorizer.evaluate_categorizer(x_val_data, y_val_data)


if __name__ == '__main__':
    train_and_store_model(evaluate=True)
