import learning.mm_services.redshift_handler as rh
from learning.utils import striphtml
import json
from collections import defaultdict
from learning import config
import traceback
import sys


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
           lead as lead,
           listagg('"' + categories.category_name + '"', ','::text) categories,
           listagg('"' + categories.category_hierarchical_id + '"', ','::text) category_ids,
           max(nr_of_usages) as nr_of_usages
    FROM cs_articles
    INNER JOIN cs_article_categories2 ON cs_articles.article_pk = cs_article_categories2.article_pk
    INNER JOIN categories ON categories.category_hierarchical_id = cs_article_categories2.category_hierarchical_id
    WHERE publish_at > '2018-10-01'::DATE AND text IS NOT NULL AND headline IS NOT NULL
    GROUP BY 1,2,3,4
    LIMIT %(limit)i
    OFFSET %(offset)i
  """ % {
        'limit': limit,
        'offset': offset
    })

    categories = defaultdict(int)
    articles_result = []
    for i, article in enumerate(articles):
        try:
            article['text'] = striphtml(article['text'])
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


def main(output_file_name, categories_file_name, stop_words_file_name):
    articles, categories = getArticles()
    print(categories)

    open(stop_words_file_name, 'a').close()

    fp = open(categories_file_name, 'w')
    for k in categories.keys():
        fp.write(k + '\n')

    fp.close()

    json.dump({
        'articles': list(articles)
    }, open(output_file_name, 'w'))

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
           body as text,
           headline as headline,
           lead as lead,
           listagg('"' + categories.category_name + '"', ','::text) categories,
           listagg('"' + categories.category_hierarchical_id + '"', ','::text) category_ids,
           max(nr_of_usages) as nr_of_usages
    FROM cs_articles
    INNER JOIN cs_article_categories2 ON cs_articles.article_pk = cs_article_categories2.article_pk
    INNER JOIN categories ON categories.category_hierarchical_id = cs_article_categories2.category_hierarchical_id
    WHERE publish_at > '2018-10-01'::DATE AND text IS NOT NULL AND headline IS NOT NULL
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
        #if len(article_text.split()) < 100:
        #    print(article['article_uuid'])
        #    break


def get_arg(index):
    try:
        sys.argv[index]
    except IndexError:
        if index == 1:
            return config.data['path'] + config.data['articles']
        else:
            if index == 2:
                return config.data['path']+ config.data['target_categories']
            else:
                if index == 3:
                    return config.data['path'] + config.data['stop_words']
                else:
                    return ''
    else:
        return sys.argv[index]

if __name__ == '__main__':
    get_short_uuid()
    #main(output_file_name=get_arg(1), categories_file_name=get_arg(2), stop_words_file_name=get_arg(3))
