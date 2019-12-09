# -*- coding: utf-8 -*-
from dotenv import load_dotenv, find_dotenv

from flask import Flask, request, Response
from flask_cors import CORS

import datetime
import os
import json

import web.tasks
import learning.model as model
from learning.mm_services import content_service
from web.categorizer_service import categorize_text, CategorizingArticleException, AppException

load_dotenv(find_dotenv())
app = Flask(__name__, static_folder='/', static_url_path='/sps', template_folder='pages')
CORS(app)

def create_response(content, status, mimetype="application/json"):
    response = Response(response=str(content),
                        status=status, mimetype=mimetype)
    response.headers["Content-Type"] = mimetype
    return response


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
    article_json = json.loads(article)

    categories = None
    article_id = None

    text = article_json['headline'] + " " + article_json['body']
    categories = article_json['category_hierarchical_ids']
    article_id = article_json.get('uuid', None)

    prediction = categorize_text(text)
    store_prediction(text, prediction, categories, article_id)
    return create_response(json.dumps({
        'category': prediction['category']
        # **prediction
    }), 200)


@app.errorhandler(AppException)
def handle_invalid_usage(error):
    return create_response(json.dumps(error.to_dict()),
                           status=error.status_code)


if __name__ == '__main__':
    web.tasks.start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
    web.tasks.stop()
