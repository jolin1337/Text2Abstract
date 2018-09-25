# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Response
from flask_cors import CORS
import os
import json

import polyglot.text
from keras.models import model_from_json

import learning.model as model
from learning.mm_services import content_service
from learning.utils import striphtml
from learning import config

app = Flask(__name__, static_folder='/', static_url_path='/sps', template_folder='pages')
CORS(app)
model_file = config.model['categorization_model']
categorizer = model.Categorizer(model_file, deterministic=True)

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
  entities = polyglot.text.Text(text).entities
  texts = [text]
  if config.model['categorizer_params']['use_ner']:
    texts = model.replace_entities(texts)
  prediction = categorizer.categorize_text(texts)[0]
  categories = [ {'category_name': c, 'category_probability': p } for c, p in prediction.items() ]
  categories.sort(key=lambda c: c['category_name'])
  category = max(categories, key=lambda c: c['category_probability'])
  return {
    'category': category,
    'categoreis': prediction,
    # 'text': text,
    'entities': [{
      'tag': ent.tag,
      'words': ent,
      'start_word_index': ent.start,
      'end_word_index': ent.end
    } for ent in entities],
    'classified_text': striphtml(text)
  }

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
    text = request.data.decode('utf-8')
    return create_response(json.dumps({
        **categorize_text(text)
    }), 200)

@app.errorhandler(AppException)
def handle_invalid_usage(error):
  print(json.dumps(error.to_dict()))
  return create_response(json.dumps(error.to_dict()),
                         status=error.status_code)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
