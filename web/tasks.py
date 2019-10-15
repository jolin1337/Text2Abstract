import datetime
import os
import json
from glob import glob

import timeloop
from learning.mm_services import redshift_handler


tl = timeloop.Timeloop()


@tl.job(interval=datetime.timedelta(minutes=10))
def store_prediction():
    print("Storing predictions...")
    # Take previously 10 minutes
    now = datetime.datetime.now()
    time = (now - datetime.timedelta(minutes=now.minute % 10 - 10,
                                     seconds=now.second,
                                     microseconds=now.microsecond)).strftime("%Y-%m-%d_%H-%M")
    for time_name in glob('./predictions/*'):
        if time_name == time:
            continue
        for fname in glob(time_name + '/*'):
            raw = open(fname, 'r').read()
            predictions = json.loads(raw)['predictions']
            data = []
            for pred in predictions:
                data.append({
                  'article_uuid': pred['article_id'],
                  'raw_info': raw,
                  'text': pred['text'],
                  'prediction': json.dumps(pred['prediction']),
                  'entities': json.dumps(pred['prediction']['entities']),
                  'predicted_category': pred['prediction']['category']['category_name'],
                  'predicted_probability': pred['prediction']['category']['category_probability'],
                  'previous_categories': json.dumps(pred['categories'])
                })
            print(len(json.dumps(data)))
            redshift_handler.insert_into('auto_categorization_predictions', data)
            os.remove(fname)
            print(fname)


def start(block=False):
    redshift_handler.setup_table('auto_categorization_predictions', {
      'article_uuid': 'VARCHAR(250)',
      'raw_info': 'VARCHAR(10000)',
      'text': 'VARCHAR(10000)',
      'prediction': 'VARCHAR(2000)',
      'entities': 'VARCHAR(2000)',
      'predicted_category': 'VARCHAR(250)',
      'predicted_probability': 'FLOAT',
      'previous_categories': 'VARCHAR(1000)'
    })
    tl.start(block)

def stop():
    tl.stop()
