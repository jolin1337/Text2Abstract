import mm_services.redshift_handler as rh
import re
import json


html_pattern = re.compile(r'<.*?>')
meta_pattern = re.compile(r'[.*?]')
dspaces_pattern = re.compile(r' +')
def striphtml(data):
  html_cleared = html_pattern.sub(' ', data)
  meta_cleared = meta_pattern.sub(' ', html_cleared)
  dspaces_cleared = dspaces_pattern.sub(' ', meta_cleared)
  return dspaces_cleared

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


def getArticles(limit=100000, offset=0):
  categories = getCategories()
  articles = rh.run_query("""
    SELECT uuid,
           data->>'headline' as headline,
           data->>'body' as text,
           data->'categories'->0->0->>'name' as top_category
    FROM public.articles
    WHERE json_array_length(data->'categories'->0) = 1
      AND data->>'body' IS NOT NULL
      AND data->>'headline' IS NOT NULL
      AND data->'categories'->0->0->>'name' IN (%(categories)s)
      AND publish_at > '2017-08-01'::timestamp
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
    except:
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
