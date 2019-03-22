# -*- coding: utf-8 -*-
from learning.logger import log
import keras
import numpy as np
import pandas
import pickle
from learning.utils import striphtml, split_train_validation_data, f1_score, offset_binary_accuracy
from learning.word2vec_model import Word2vecModel
from learning.doc2vec_model import Doc2vecModel

pandas.set_option('display.expand_frame_repr', False)


class Categorizer(object):
    def __init__(self, vec_model, model_file=None):
        self.vec_model = vec_model
        if model_file is not None:
            self.load_model(model_file)
            log("Loaded model with %s categories" % ",".join(self.categories))
        else:
            self.model = None
        self.timestep = 200
        self.epochs = 15

    def preprocess_text(self, texts, labels):
        log("Preprocess text")
        document_texts = [keras.preprocessing.text.text_to_word_sequence(striphtml(text))
                      for text in texts]
        for doc, label in zip(document_texts, labels):
            if not doc: continue
            if isinstance(self.vec_model, Doc2vecModel):
                vectors = np.zeros([self.timestep, self.vec_model.vector_size()])
                for i in range(self.timestep):
                    if len(doc) < self.timestep * i:
                        break
                    vec = self.vec_model.infer_vector(doc[i*self.timestep:(i+1)*self.timestep])
                    vectors[i] = vec
                yield vectors, label
            elif isinstance(self.vec_model, Word2vecModel):
                vec = self.vec_model.infer_vector(doc[:self.timestep])
                pad_length = max(0, self.timestep - len(doc))
                if pad_length > 0:
                    pad_vector = np.zeros([pad_length,self.vec_model.vector_size()])
                    vec = np.append(vec, pad_vector, axis=0)
                yield vec, label

    def categorize_text(self, text):
        if self.model == None:
            raise UnknownModelException()
        processed_text = np.array(self.preprocess_text(text))
        probas = self.model.predict([processed_text])
        return [{
            c: float(p)
            for c, p in zip(self.categories, list(proba))
        } for proba in probas]

    def construct_model(self, categories):
        raise "Not implemented"

    def train_categorizer(self, x_data, y_data, split_train_val=0.9, **model_args):
      self.categories = list(set(c for y in y_data for c in y))
      y_data = [[self.categories.index(c) for c in y] for y in y_data]
      y_data_one_hot = encode_n_hot_vectors(y_data)
      x_data_processed, y_data_one_hot_processed = zip(*list(self.preprocess_text(x_data, y_data_one_hot)))
      x_train, y_train, x_val, y_val = split_train_validation_data(split_train_val, x_data_processed, y_data_one_hot_processed)

      log("Done preprocessing data")
      model = self.construct_model(self.categories)
      model.compile(loss='categorical_crossentropy',
                    optimizer='rmsprop',
                    metrics=['accuracy', f1_score])
      log("Labels: ", self.categories)
      model.fit([np.array(x_train)], [np.array(y_train)], validation_data=([np.array(x_val)], [np.array(y_val)]),
                **{'epochs': self.epochs, **model_args})
      return model

    def evaluate_categorizer(self, x_data, y_data):
        if not self.model:
            raise Exception("No model defined do evaluate")
        self.model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy', f1_score])
        y_data = [[self.categories.index(c) for c in y] for y in y_data]
        y_data_one_hot = np.array(encode_n_hot_vectors(y_data, self.categories))
        x_data_processed, y_data_one_hot_processed = zip(*list(self.preprocess_text(x_data, y_data_one_hot)))
        evaluation = self.model.evaluate([np.array(x_data_processed)], [np.array(y_data_one_hot_processed)])
        log({name: val for name, val in zip(self.model.metrics_names, evaluation)})

        # Predict all values of validation data
        prediction = self.model.predict([np.array(x_data_processed)])
        true_positives = len([x
                               for index, x in enumerate(prediction)
                               if x.argmax() in [i for i, y in enumerate(y_data_one_hot_processed[index]) if y == 1.0]])
        total_predictions = len(prediction)
        log("Accuracy %f" % (true_positives / total_predictions,))

        # Compute confusion matrix of validation data
        predicted_values = [[1 if np.argmax(x) == i else 0 for i, v in enumerate(x)] for x in prediction]
        true_values = [[1 if np.argmax(x) == i else 0 for i, v in enumerate(x)] for x in y_data_one_hot_processed]
        confusion_matrix = np.zeros((len(true_values[0]), len(true_values[0])))
        for i in range(len(confusion_matrix)):
            for j in range(len(confusion_matrix)):
                confusion_matrix[i][j] = len([1 for k, y in enumerate(true_values) if np.argmax(predicted_values[k]) == i and y[j] == 1])
        pandas.set_option('display.expand_frame_repr', False)
        cf = pandas.DataFrame(confusion_matrix, index=self.categories, columns=self.categories)
        cf.loc['sum'] = cf.sum(numeric_only=True, axis=0)
        cf['sum'] = cf.sum(numeric_only=True, axis=1)
        log(cf)

    def load_model(self, path):
        obj = pickle.load(open(path + '.pkl', 'rb'))
        self.categories = obj['categories']
        self.vec_model = obj['vec_model']
        self.model = keras.models.model_from_json(obj['model_json'])
        self.model.load_weights(path + '.model.h5')
        self.model._make_predict_function()
        self.epochs = obj['epochs']
        self.n_layers = obj['n_layers']
        self.timestep = obj['timestep']

    def save_model(self, path):
        obj = {
            'categories': self.categories,
            'vec_model': self.vec_model,
            'model_json': self.model.to_json(),
            'epochs': self.epochs,
            'n_layers': self.n_layers,
            'timestep': self.timestep
        }
        self.model.save_weights(path + '.model.h5')
        pickle.dump(obj, open(path + '.pkl', 'wb'))


def encode_n_hot_vectors(y_data, categories=None):
    categories = categories or list(set(c for y in y_data for c in y))
    y_data_one_hot = np.zeros((len(y_data), len(categories)))
    for i, y in enumerate(y_data_one_hot):
        y[y_data[i]] = 1
    return y_data_one_hot



