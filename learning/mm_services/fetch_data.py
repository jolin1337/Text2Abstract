import mm_services.redshift_handler as rh
import json
from utils import striphtml
import traceback

def getArticles(limit=500000, offset=0):
  articles = rh.run_query("""
    WITH categories AS (
      SELECT category_hierarchical_id, category_name, count(*) as nr_of_usages
      FROM cs_article_categories2
      WHERE category_hierarchical_id IS NOT NULL
        AND length(category_hierarchical_id) = 7 -- allow only top categories for now
      GROUP BY 1, 2
      HAVING count(*) > 500
    )
    SELECT article_uuid,
           body as text,
           headline as headline,
           listagg('"' + categories.category_name + '"', ','::text) categories,
           listagg('"' + categories.category_hierarchical_id + '"', ','::text) category_ids,
           max(nr_of_usages) as nr_of_usages
    FROM cs_articles
    INNER JOIN cs_article_categories2 ON cs_articles.article_pk = cs_article_categories2.article_pk
    INNER JOIN categories ON categories.category_hierarchical_id = cs_article_categories2.category_hierarchical_id
    WHERE publish_at > '2018-10-01'::DATE AND text IS NOT NULL AND headline IS NOT NULL
    GROUP BY 1,2,3
    LIMIT %(limit)i
    OFFSET %(offset)i
  """ % {
    'limit': limit,
    'offset': offset
  })
  categories = set()
  for i, article in enumerate(articles):
    try:
      article['text'] = striphtml(article['text'])
      article['headline'] = striphtml(article['headline'])
      article['categories'] = list(set([cs for cs in article['categories'][1:-1].split('","')]))
      article['category_ids'] = list(set([cs for cs in article['category_ids'][1:-1].split('","')]))
      categories.update(article['categories'])
    except:
      traceback.print_exc()
      print("Error here: ", i, article)
      continue
    yield article
  print(categories)

def main(output_file_name):
  articles = getArticles()
  json.dump({
    'articles': list(articles)
  }, open(output_file_name, 'w'))

if __name__ == '__main__':
  main(output_file_name=sys.argv[2])
