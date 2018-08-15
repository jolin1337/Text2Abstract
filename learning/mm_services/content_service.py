import requests
import json
import os
from dateutil import parser as dateparser

def get_cs_headers():
    return {
        'content-type': "application/json",
        'accept': "application/json",
        'authorization': "Token token=" + os.environ.get("CS_TOKEN")
    }

def find_article(uuid, json_articles):
    article = [article for article in json_articles if article['uuid'] == uuid]
    if article:
        return article[0]
    return None

def search_articles(uuids):
  uuids = list(uuids)
  if len(uuids) == 0: return []
  unique_uuids = list(set(uuids))
  url = os.environ.get('CS_URL')
  querystring = {
      'published': 'true',
      'uuids[]': unique_uuids}
  response = requests.request("GET", url, headers=get_cs_headers(), params=querystring, timeout=1)
  try:
      json_articles = json.loads(response.text)['articles']
      for uuid in uuids:
        article = find_article(uuid, json_articles)
        if article is None: continue
        article['pub_date'] = dateparser.parse(article['pub_date'])
        yield article
  except Exception as e:
    print(url, querystring, response.text, response.status_code)
    import traceback
    print(traceback.format_exc())
    print("Error in request to CS, application continues")
  return []


