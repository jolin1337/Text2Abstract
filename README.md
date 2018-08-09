# Auto categorizer
This project aims to create a self learning application that can detect the subject of a text. The algorithm consists of three steps.

* Preprocessing text by filter out non words, strip HTML, identify nouns and verbs, replace Entities with tag names
* Train a doc2vec model that converts the input text into a document vector to be used in the categorization step
* Train a categorizer with LSTM model by feeding the processed training data through the doc2vec model -> LSTM model

This work is a clean version of the project described [here](https://docs.google.com/document/d/1ZHMNeUQRR3IWkfcevRcvv7by5D71AYpK3F3YRKLVlGE/edit) and the github repository [here](https://github.com/jolin1337/Text2Abstract)


## To install
Navigate to the folder you want to have the project
```
$ git clone <url> auto-categorizer
$ cd auto-categorizer
$ python -m venv ./venv
$ ln -s venv/lib/python3.5/site-packages/learning learning
$ python -m pip install -r requirements.txt
$ curl https://drive.google.com/uc?export=download&id=FILE_ID
$ tar -xvzf trained-models.tar.gz
$ cp .env.sample .env
### Add SOLDR_TOKEN in .env file and do
$ source .env
```

## To train
All training parameters are currently in the model file `learning/model.py`
```
$ python learning/model.py
```

## To run a local webservice
```
$ python web/app.py
```
