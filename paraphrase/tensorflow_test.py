#!/bin/bash
# -*- coding: utf-8 -*-
'''
A Recurrent Neural Network (LSTM) implementation example using TensorFlow library.
This example is using the MNIST database of handwritten digits (http://yann.lecun.com/exdb/mnist/)
Long Short Term Memory paper: http://deeplearning.cs.cmu.edu/pdfs/Hochreiter97_lstm.pdf
Author: Aymeric Damien
Project: https://github.com/aymericdamien/TensorFlow-Examples/
'''

from __future__ import print_function
import sys
sys.path.append('../gensim')
import dotenv
dotenv.load()

import random
import tensorflow as tf
from tensorflow.contrib import rnn
import numpy as np

# Import MNIST data
from tensorflow.examples.tutorials.mnist import input_data
import gensim_documents
from PyTeaser.pyteaser import Summarize
# "lead"
# "title"
# Summarize("title", "body")
class SubData(object):
	"""docstring for SubData"""
	def __init__(self, X, Y):
		self.images = X
		self.labels = Y
		self.prev_count = 0
	def next_batch(self, batch_size):
		toReturn = (self.images[self.prev_count:self.prev_count+batch_size], self.labels[self.prev_count:self.prev_count+batch_size])
		self.prev_count += batch_size
		return toReturn

class DataClass(object):
	"""docstring for DataClass"""
	def __init__(self, splitTrainSize, splitTestSize):
		self.splitTrainSize = splitTrainSize
		self.splitTestSize = splitTestSize
		self.text_to_ids = {}
		self.ids_to_text = {}
		self.X = []
		self.Y = []
		self.current_document_id = 0
	def read_data(self, dataSource):
		headings = False
		for i, line in enumerate(open(dataSource, 'r')):
			if i >= 10000:
				break
			attrs = line[1:-2].split('"§§"')
			if headings == False:
				headings = {attr: index for index, attr in enumerate(attrs)}
				continue
			for word in attrs[headings["lead"]].split() + attrs[headings["title"]].split() + attrs[headings["body"]].split():
				if not word in self.ids_to_text:
					self.text_to_ids[word] = self.current_document_id
					self.ids_to_text[self.current_document_id] = word
					self.current_document_id += 1
			self.X.append([self.text_to_ids[word] for word in ' '.join(Summarize(attrs[headings["title"]], attrs[headings["body"]], 3)).split()])
			self.Y.append([self.text_to_ids[word] for word in attrs[headings["lead"]].split()])
		indicies = range(0, len(self.X)-1)
		random.shuffle(indicies)
		X = np.array(self.X)
		Y = np.array(self.Y)
		trainLength = int(len(X)*self.splitTrainSize)
		testLength = int(trainLength + len(X)*self.splitTestSize)
		self.train = SubData(X[indicies[0:trainLength]], Y[indicies[0:trainLength]])
		self.test = SubData(X[indicies[trainLength:testLength]], Y[indicies[trainLength:testLength]])
		self.validation = SubData(X[indicies[testLength:]], Y[indicies[testLength:]])

mnist = DataClass(0.75, 0.2)#input_data.read_data_sets("/tmp/data/", one_hot=True) #
mnist.read_data(dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_april_16_1205-filter-uuid')

'''
To classify images using a recurrent neural network, we consider every image
row as a sequence of pixels. Because MNIST image shape is 28*28px, we will then
handle 28 sequences of 28 steps for every sample.
'''

# Parameters
learning_rate = 0.001
training_iters = 100000
batch_size = 128
display_step = 10

# Network Parameters
n_input = 28 # MNIST data input (img shape: 28*28)
n_steps = 28 # timesteps
n_hidden = 128 # hidden layer num of features
n_classes = 10 # MNIST total classes (0-9 digits)

# tf Graph input
x = tf.placeholder("float", [None, n_steps, n_input])
y = tf.placeholder("float", [None, n_classes])

# Define weights
weights = {
    'out': tf.Variable(tf.random_normal([n_hidden, n_classes]))
}
biases = {
    'out': tf.Variable(tf.random_normal([n_classes]))
}


def RNN(x, weights, biases):

    # Prepare data shape to match `rnn` function requirements
    # Current data input shape: (batch_size, n_steps, n_input)
    # Required shape: 'n_steps' tensors list of shape (batch_size, n_input)

    # Unstack to get a list of 'n_steps' tensors of shape (batch_size, n_input)
    x = tf.unstack(x, n_steps, 1)

    # Define a lstm cell with tensorflow
    lstm_cell = rnn.BasicLSTMCell(n_hidden, forget_bias=1.0)

    # Get lstm cell output
    outputs, states = rnn.static_rnn(lstm_cell, x, dtype=tf.float32)

    # Linear activation, using rnn inner loop last output
    return tf.matmul(outputs[-1], weights['out']) + biases['out']

pred = RNN(x, weights, biases)

# Define loss and optimizer
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=pred, labels=y))
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)
# optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(cross_entropy)

# Evaluate model
correct_pred = tf.equal(tf.argmax(pred,1), tf.argmax(y,1))
accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

# Initializing the variables
init = tf.global_variables_initializer()

# Launch the graph
with tf.Session() as sess:
    sess.run(init)
    step = 1
    # Keep training until reach max iterations
    while step * batch_size < training_iters:
        batch_x, batch_y = mnist.train.next_batch(batch_size)
        # Reshape data to get 28 seq of 28 elements
        #batch_x = batch_x.reshape((batch_size, n_steps, n_input))

        # Run optimization op (backprop)
        sess.run(optimizer, feed_dict={x: batch_x, y: batch_y})
        if step % display_step == 0:
            # Calculate batch accuracy
            acc = sess.run(accuracy, feed_dict={x: batch_x, y: batch_y})
            # Calculate batch loss
            loss = sess.run(cost, feed_dict={x: batch_x, y: batch_y})
            print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
                  "{:.6f}".format(loss) + ", Training Accuracy= " + \
                  "{:.5f}".format(acc))
        step += 1
    print("Optimization Finished!")

    # Calculate accuracy for 128 mnist test images
    test_len = 128
    test_data = mnist.test.images[:test_len].reshape((-1, n_steps, n_input))
    test_label = mnist.test.labels[:test_len]
    print("Testing Accuracy:", \
        sess.run(accuracy, feed_dict={x: test_data, y: test_label}))