import learning.mm_services.redshift_handler as rh
from learning.utils import striphtml
import jsonlines
from collections import defaultdict
from learning import config
import traceback
import sys


def getArticles(category_hierarchical_prefix, limit=500000, offset=0):
    articles = rh.run_query("""
    WITH categories AS (
      SELECT category_hierarchical_id, category_name, count(*) as nr_of_usages
      FROM cs_article_categories2
      WHERE category_hierarchical_id LIKE '%(category_hierarchical_prefix)s%%'
      GROUP BY category_hierarchical_id, category_name
      HAVING count(*) > 500
    )
    SELECT article_uuid,
           body,
           headline,
           lead,
           listagg('"' + categories.category_name + '"', ','::text) categories,
           listagg('"' + categories.category_hierarchical_id + '"', ','::text) category_ids,
           max(nr_of_usages) as nr_of_usages
    FROM cs_articles
    INNER JOIN cs_article_categories2 ON cs_articles.article_pk = cs_article_categories2.article_pk
    INNER JOIN categories ON categories.category_hierarchical_id = cs_article_categories2.category_hierarchical_id
    WHERE publish_at > '2018-10-01'::DATE AND body IS NOT NULL AND headline IS NOT NULL
    GROUP BY 1,2,3,4
    LIMIT %(limit)i
    OFFSET %(offset)i
  """ % {
        'limit': limit,
        'offset': offset,
        'category_hierarchical_prefix': category_hierarchical_prefix
    })

    categories = defaultdict(int)
    articles_result = []
    for i, article in enumerate(articles):
        try:
            article['body'] = striphtml(article['body'])
            article['lead'] = striphtml(article['lead'])
            article['headline'] = striphtml(article['headline'])
            article['categories'] = list(set([cs for cs in article['categories'][1:-1].split('","')]))
            article['category_ids'] = list(set([cs for cs in article['category_ids'][1:-1].split('","')]))
            for cat in article['categories']:
                categories[cat] += 1
        except:
            traceback.print_exc()
            print("Error here: ", i, article)
            continue
        articles_result.append(article)

    return articles_result,categories


def main(category_level):
    model = config.model['categorization_model_' +
                 str(category_level)]
    prefix = model['category_hierarchical_prefix']
    print(prefix)
    articles, categories = getArticles(prefix)
    print(categories)

    with jsonlines.open(model['articles'], mode='w') as writer:
      writer.write_all(list(articles))

def get_short_uuid(limit=5000, offset=0):
    print('Before executing query')
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
           body,
           headline,
           lead,
           listagg('"' + categories.category_name + '"', ','::text) categories,
           listagg('"' + categories.category_hierarchical_id + '"', ','::text) category_ids,
           max(nr_of_usages) as nr_of_usages
    FROM cs_articles
    INNER JOIN cs_article_categories2 ON cs_articles.article_pk = cs_article_categories2.article_pk
    INNER JOIN categories ON categories.category_hierarchical_id = cs_article_categories2.category_hierarchical_id
    WHERE publish_at > '2018-10-01'::DATE AND body IS NOT NULL AND headline IS NOT NULL
    GROUP BY 1,2,3,4
    LIMIT %(limit)i
    OFFSET %(offset)i
    """ % {
        'limit': limit,
        'offset': offset
    })

    print('After executing query')
    for i, article in enumerate(articles):
        try:
            article['text'] = striphtml(article['text'])
            article_text = striphtml(article['text'])
            if len(article_text.split()) < 15:
                print("Hej")
                print('article_uuid = '+article['article_uuid'])
                break
        except:
            traceback.print_exc()
            print("Error here: ", i, article)
            continue

if __name__ == '__main__':
    main(sys.argv[1])
