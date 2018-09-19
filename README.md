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
$ git checkout productified-version
$ python -m venv ./venv
$ ln -s venv/lib/python3.5/site-packages/learning learning
$ python -m pip install -r requirements.txt
$ wget https://drive.google.com/uc?export=download&confirm=no_antivirus&id=12ewf6e2JrElKJRTsfd8S_cSuj4kiQipZ
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

## To run sagemaker docker container
```
$ ./build_and_push.sh sagemaker-auto-categorization
# Then open notebook and train the model or create an endpoint starting jupyter:
$ jupyter notebook
```
