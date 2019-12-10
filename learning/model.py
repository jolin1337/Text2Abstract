# -*- coding: utf-8 -*-
import numpy as np
import keras

import jsonlines
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


# Limits the category articles to not exceed the category with the fewest articles
def limit_article_groups_to_minimum_category_size(articles):
    available_category_counts = collections.Counter([cat for x, y in articles for cat in y])
    min_category_count = available_category_counts.most_common()[-1][1]
    current_category_counts = {cat: 0 for cat in available_category_counts.keys()}

    for text,categories in articles:
        text = text.strip()
        if text == '':
            continue

        categories = [c for c in categories if current_category_counts[c] < min_category_count]
        if not categories:
            continue

        for cat in categories:
            current_category_counts[cat] += 1

        yield text,categories


def filter_articles_category_quantity(articles, threshold):
    articles = list(articles)
    all_categories = [c for x, y in articles for c in y]
    quantity = collections.Counter(all_categories)
    for text, categories in articles:
        categories = [c for c in categories if quantity[c] >= threshold]
        if not categories:
            continue
        yield text, categories


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
    return limit_article_groups_to_minimum_category_size(data, non_location_categories)


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


def filter_article_category_lengths(articles, category_level):
    """Remove categories that have are not of the right length for the level"""
    category_hierarchical_id_length = (category_level + 1) * 3 + category_level
    for article, categories in articles:
        categories = list(filter(lambda x: len(x) == category_hierarchical_id_length, categories))
        if len(categories) == 0:
            continue
        yield article, categories

def get_articles(category_level):
    file = open(config.data['path'] + config.model['categorization_model_' + str(category_level)]['articles'], 'r', encoding='utf-8')
    reader = jsonlines.Reader(file)
    data = list(reader)
    articles = [(a['headline'] + ' ' + a['body'], a['category_ids']) for a in data]
    # articles = filter_article_category_locations(articles)
    articles = list(filter_article_category_lengths(articles, category_level))
    # articles = list(limit_article_groups_to_minimum_category_size(articles))
    articles = list(filter_articles_category_quantity(articles, 100))
    articles = list(filter_article_quantity_of_categories(articles, 1862))

    return articles


def get_vector_model(x_data=None, y_data=None, **params):
    vec_model = Word2vecModel
    if config.model['vec_model']['type'] == 'doc2vec':
        vec_model = Doc2vecModel
    random.seed(0)
    vec = None
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
    if config.model['categorization_model_4']['type'] == 'lstm':
        return LSTMCategorizer(vec, source)
    return BLSTMCategorizer(vec, source)


def train_and_store_model(evaluate=False, category_level=None):
    if category_level == None:
        raise "category_level can't be None!"
    articles = get_articles(category_level)
    random.shuffle(articles)
    log("Numer of articles:", len(articles))
    available_category_counts = collections.Counter([cat for text, categories in articles for cat in categories])
    log(available_category_counts)
    x_val_data, y_val_data, x_data, y_data = split_train_validation_data(0.1, *zip(*articles))

    log("Train vec model")
    # Train model #
    vec = get_vector_model(x_data, y_data, deterministic=True)
    callbacks = []
    log("Train categorization model")
    if config.model['categorization_model_' + str(category_level)]['model_checkpoint']:
        checkpoint = keras.callbacks.ModelCheckpoint(config.model['path'] + config.model['categorization_model_4']['model_checkpoint'],
                                                     monitor='val_loss', mode='min',
                                                     save_best_only=True, save_weights_only=True, period=5)
        tensorboard = keras.callbacks.TensorBoard(log_dir=config.model['path'] + '/Graph', histogram_freq=0, write_graph=True, write_images=True)
        callbacks = [checkpoint, tensorboard]

    categorizer = get_categorization_model(vec)
    categorizer.train_categorizer(x_data, y_data, callbacks=callbacks)
    categorizer.save_model(config.model['path'] + config.model['categorization_model_' + str(category_level)]['name'])

    if evaluate:
        log("Evaluate model")
        # Evaluate model #
        categorizer = get_categorization_model(None, config.model['path'] + config.model['categorization_model_' + str(category_level)]['name'])
        categorizer.evaluate_categorizer(x_val_data, y_val_data)


if __name__ == '__main__':
    for i in [1, 3, 4]:
        train_and_store_model(evaluate=True, category_level=i)
        config.model['vec_model']['train'] = False
