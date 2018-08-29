import mm_services.redshift_handler as rh
import json
from utils import striphtml
import traceback

def getCategories(limit=10000):
  rows = rh.run_query("""
    SELECT data->'categories'->0->0->>'name' as category,
           count(*) as nr_of_usages
    FROM public.articles
    WHERE json_array_length(data->'categories'->0) = 1
      AND publish_at > '2018-01-01'::timestamp
    GROUP BY 1
    ORDER BY 2
    LIMIT %s
  """ % (limit,), use_cache=True)
  return [row['category'] for row in rows]


def getArticles(limit=500000, offset=0):
  categories = [] # getCategories()
  articles = rh.run_query("""
    SELECT uuid,
           data->>'headline' as headline,
           data->>'body' as text,
           data->'categories' as categories,
           data->'categories'->0->0->>'name' as top_category
    FROM public.articles
    WHERE --json_array_length(data->'categories'->0) = 1
          data->>'body' IS NOT NULL
      AND data->>'headline' IS NOT NULL
      --AND data->'categories'->0->0->>'name' IN (%(categories)s)
      AND publish_at > '2017-05-10'::timestamp
    LIMIT %(limit)i
    OFFSET %(offset)i
  """ % {
    'limit': limit,
    'offset': offset,
    'categories': "'" + "','".join(categories) + "'"
  })
  for i, article in enumerate(articles):
    try:
      article['text'] = striphtml(article['text'])
      article['headline'] = striphtml(article['headline'])
      article['categories'] = list(set([cs2['name'] for cs1 in article['categories'] for cs2 in cs1]))
    except:
      traceback.print_exc()
      print("Error here: ", i, article)
      continue
    yield article

def main(file_name):
  articles = getArticles()
  json.dump({
    'articles': list(articles)
  }, open(file_name, 'w'))

if __name__ == '__main__':
  main('data/articles.json')
