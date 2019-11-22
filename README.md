# Auto categorizer
This project aims to create a self learning application that can detect the subject of a text. The algorithm consists of three steps.

* Preprocessing text by filter out non words, strip HTML, identify nouns and verbs, replace Entities with tag names
* Train a doc2vec model that converts the input text into a document vector to be used in the categorization step
* Train a categorizer with LSTM model by feeding the processed training data through the doc2vec model -> LSTM model

This work is a clean version of the project described [here](https://docs.google.com/document/d/1ZHMNeUQRR3IWkfcevRcvv7by5D71AYpK3F3YRKLVlGE/edit)


## To install
Navigate to the folder you want to have the project
```
$ git clone https://github.com/jolin1337/Text2Abstract auto-categorizer
$ cd auto-categorizer
$ python -m venv ./venv
$ ln -s venv/lib/python3.5/site-packages/learning learning
$ python -m pip install -r requirements.txt
$ cp .env.sample .env
$ export PYTHONPATH=`pwd`
### Add SOLDR_TOKEN in .env file and do
$ source .env
```

## To fetch data run
```
$ python learning/mm_services/fetch_data.py learning/data/new_metadata_articles.json
```

## Create a list of top categories, one line per category
Name it `new_top_categories.txt`

## To train
All training parameters are ported to the configuration file specified in the `config` folder
```
$ python learning/model.py
```

## To evaluate models
```
# creates a result.csv with all articles in the specified article source evaluated by the models, with the actual categories and the predicted categories
python evaluation/evaluate_models.py

# takes the result.csv and calculates different accuracies depending on the probability used for filtering out predictions.
ruby evaluation/calculate_accuracy.rb
```

## To run a local webservice
```
$ python web/app.py
```

## To run sagemaker docker container
```
$ ./build_and_push.sh sagemaker-auto-categorization
# Then open notebook and train the model or create an endpoint starting jupyter:
$ jupyter notebook
```

## For more guides look in the notebooks found in the `notebooks` folder
