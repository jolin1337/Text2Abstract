# -*- coding: utf-8 -*-
from learning.categorizer_model import Categorizer
from learning import config
import keras
import numpy as np
import pandas
import random
import json


pandas.set_option('display.expand_frame_repr', False)


class LSTMCategorizer(Categorizer):
    def __init__(self, vec_model, model_file=None):
        super().__init__(vec_model, model_file)
        self.n_layers = 10

    def construct_model(self, categories):
      num_classes = len(categories)
      ##### expected input data shape: (batch_size, timesteps, data_dim)
      input_shape = (self.timestep, self.vec_model.vector_size())
      model = keras.models.Sequential()
      model.add(keras.layers.LSTM(50,
                input_shape=input_shape,
                return_sequences=True))  # returns a sequence of vectors of dimension 50
      for layer in range(self.n_layers-2):
          model.add(keras.layers.Dropout(0.2))
          model.add(keras.layers.LSTM(50, return_sequences=True))  # returns a sequence of vectors of dimension 50
      model.add(keras.layers.LSTM(50))  # return a single vector of dimension 50
      model.add(keras.layers.Dense(num_classes, activation='softmax'))
      self.model = model
      return model

