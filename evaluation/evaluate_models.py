import csv
import json
import web.categorizer_service
import os

from multiprocessing import Pool

def categorize_text(texts, categories):
    try:
        return web.categorizer_service.categorize_texts(texts, categories)
    except web.categorizer_service.CategorizingArticleException:
        print('fail')


def write(dicts, write_header=False):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'result.csv'), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=dicts[0].keys())
        if write_header:
            writer.writeheader()
        writer.writerows(dicts)
        

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def prediction_to_dict(prediction):
    categories = []
    if len(prediction[0]) >= 1:
        categories = prediction[0]

    if len(prediction) >= 2:
        return {
            'category': ','.join(categories),
            'predicted': prediction[1][0][0],
            'probability': prediction[1][0][1],
            'backup': prediction[1][1][0],
            'backup_probability': prediction[1][1][1]
        }
    return {}


def predictions_to_dicts(predictions):
    for prediction in predictions:
        level_1 = prediction_to_dict(prediction[0])
        level_3 = prediction_to_dict(prediction[1])
        level_4 = {}

        if len(prediction[2]) == 2:
            level_4 = prediction_to_dict(prediction[2])

        yield {
            'level_1': level_1['category'],
            'predicted_1': level_1['predicted'],
            'probability_1': level_1['probability'],
            'backup_1': level_1['backup'],
            'backup_probability_1': level_1['backup_probability'],
            'level_3': level_3.get('category', None),
            'predicted_3': level_3.get('predicted', None),
            'probability_3': level_3.get('probability', None),
            'backup_3': level_3.get('backup', None),
            'backup_probability_3': level_3.get('backup_probability', None),
            'level_4': level_4.get('category', None),
            'predicted_4': level_4.get('predicted', None),
            'probability_4': level_4.get('probability', None),
            'backup_4': level_4.get('backup', None),
            'backup_probability_4': level_4.get('backup_probability', None),
        }

def predict(articles):
    articles = list(filter(lambda a: len(a["body"]) > 400, articles))

    texts = list(map(lambda a: a['headline'] + ' ' + a['body'], articles))
    categories = list(map(lambda a: a['category_ids'], articles))

    predictions = categorize_text(texts, categories)
    predictions = list(
        zip(predictions[1], predictions[3], predictions[4]))
    predictions = list(predictions_to_dicts(predictions))
    for i in range(len(predictions)):
        predictions[i]['text'] = texts[i]

    return predictions

if __name__ == '__main__':
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../learning/data/RYF-QPR_articles.jsonl')
    counter = 0
    write_header = True
    with open(data_path, 'r', encoding='utf-8') as file:
        for lines in batch(file.readlines(), 2000):
            articles = list(map(lambda l: json.loads(l), lines))
            predictions = predict(articles)
            counter += len(predictions)
            print(counter)
            
            write(predictions, write_header)
            write_header = False
