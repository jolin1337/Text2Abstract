# -*- coding: utf-8 -*-

from flask import Flask, request, render_template, Response
from flask_cors import CORS
import os
import json
from dateutil import parser as dateparser

import learning.model as model
from learning.mm_services import content_service
from keras.models import model_from_json

app = Flask(__name__, static_folder='/', static_url_path='/sps', template_folder='pages')
CORS(app)
model_path = os.environ.get('MODEL_PATH')
categorizer = model.load_model(model_path + '/lstm-categorizer.model', deterministic=True)

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
  response.headers["Content-Type"] = "application/json"
  return response


@app.route('/categorize-by-uuid')
def categorize_by_uuid():
  uuid = request.args.get('uuid')
  found_articles = content_service.search_articles([uuid])
  article = content_service.find_article(uuid, found_articles)
  if article:
    return create_response(json.dumps(categorizer.categorize_text([article['body']])), 200)
  raise CategorizingArticleException("No article found with uuid: %s" % (uuid,), 400)

@app.route('/categorize')
def categorize():
  prediction = categorizer.categorize_text([request.args.get('text')])
  categories = [ {'category_name': c, 'category_probability': p } for c, p in prediction.items() ]
  categories.sort(key=lambda c: c['category_name'])
  category = max(categories, key=lambda c: c['category_probability'])
  return create_response(json.dumps({
    'category': category['category_name'],
    'categories': prediction
  }), 200)

@app.errorhandler(AppException)
def handle_invalid_usage(error):
  print(json.dumps(error.to_dict()))
  return create_response(json.dumps(error.to_dict()),
                         status=error.status_code)

if __name__ == '__main__':
    app.run()
