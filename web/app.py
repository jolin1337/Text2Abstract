# -*- coding: utf-8 -*-
from dotenv import load_dotenv, find_dotenv

from flask import Flask, request, Response
from flask_cors import CORS

import datetime
import os
import json

import web.tasks
import learning.model as model
from learning.categorizer_model import Categorizer
from learning.word2vec_model import Word2vecModel
from learning.doc2vec_model import Doc2vecModel
from learning.mm_services import content_service
from learning.utils import striphtml
from learning import config

load_dotenv(find_dotenv())
app = Flask(__name__, static_folder='/', static_url_path='/sps', template_folder='pages')
CORS(app)
if config.model['vec_model']['type'] == 'doc2vec':
    VecModel = Doc2vecModel
else:
    VecModel = Word2vecModel
vec_file = config.model['path'] + config.model['vec_model']['name']
model_file = config.model['path'] + config.model['categorization_model']['name']
vec_model = VecModel(vec_file, deterministic=True)
categorizer = Categorizer(vec_model, model_file)
min_word_count = config.data.get('min_word_count', 10)


class AppException(Exception):
    def __init__(self, message, status_code):
        super(AppException, self).__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {
            'message': self.message
        }


class CategorizingArticleException(AppException):
    def __init__(self, *argv, **argd):
        super().__init__(*argv, **argd)

    def to_dict(self):
        return {
            **super().to_dict(),
            "error": "Categorizing article"
        }


def create_response(content, status, mimetype="application/json"):
    response = Response(response=str(content),
                        status=status, mimetype=mimetype)
    response.headers["Content-Type"] = mimetype
    return response


def categorize_text(text):
    texts = [text]
    entities = []

    if len(striphtml(text).split()) < min_word_count:
        raise CategorizingArticleException("Too few words in text to make a categorization", 400)

    prediction = categorizer.categorize_text(texts)[0]
    categories = [{'category_name': c, 'category_probability': p} for c, p in prediction.items()]
    categories.sort(key=lambda c: c['category_name'])
    category = max(categories, key=lambda c: c['category_probability'])
    return {
        'category': category,
        'categories': prediction,
        'entities': [{
            'tag': ent.tag,
            'words': ent,
            'start_word_index': ent.start,
            'end_word_index': ent.end
        } for ent in entities],
        'classified_text': striphtml(text)
    }


def store_prediction(text, prediction, categories, article_id):
    now = datetime.datetime.now()
    time = (now - datetime.timedelta(minutes=now.minute % 10,
                                     seconds=now.second,
                                     microseconds=now.microsecond)).strftime("%Y-%m-%d_%H-%M")
    os.makedirs('predictions/' + time, exist_ok=True)
    number = 1
    while True:
        hist = {'predictions': []}
        if os.path.isfile('predictions/%s/%d' % (time, number)):
            number += 1
            continue
        hist['predictions'].append({
            'text': text,
            'prediction': prediction,
            'categories': categories,
            'article_id': article_id
        })
        json.dump(hist, open('predictions/%s/%d' % (time, number), 'w', encoding='utf-8'))
        break


@app.route('/categorize-by-uuid')
def categorize_by_uuid():
    uuid = request.args.get('uuid')
    found_articles = content_service.search_articles([uuid])
    article = content_service.find_article(uuid, found_articles)
    if article:
        return create_response(json.dumps({
            **categorize_text(article['body']),
            'articleUuid': uuid
        }), 200)

    raise CategorizingArticleException("No article found with uuid: %s" % (uuid,), 400)


@app.route('/categorize')
def categorize():
    text = request.args.get('text')
    return create_response(json.dumps({
        **categorize_text(text)
    }), 200)


@app.route('/ping', methods=['GET'])
def ping():
    """Determine if the container is working and healthy. In this sample container, we declare
    it healthy if we can load the model successfully."""
    # You can insert a health check here
    health = True
    status = 200 if health else 404
    return Response(response='\n', status=status, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def transformation():
    article = request.data.decode('utf-8')
    categories = None
    article_id = None
    try:
        article_json = json.loads(article)
        # TODO: Add lead and maybe title to the text
        text = article_json['body']
        categories = article_json['categories2']
        article_id = article_json['uuid']
    except:
        text = article

    prediction = categorize_text(text)
    store_prediction(text, prediction, categories, article_id)
    return create_response(json.dumps({
        **prediction
    }), 200)


@app.errorhandler(AppException)
def handle_invalid_usage(error):
    return create_response(json.dumps(error.to_dict()),
                           status=error.status_code)


if __name__ == '__main__':
    web.tasks.start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
    web.tasks.stop()
