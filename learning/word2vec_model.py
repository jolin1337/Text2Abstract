import os
import random
import gensim
import re
import config
import jieba
import numpy as np
from logger import log

def loadStopWords(filepath):
  stopwords = [line.strip() for line in open(filepath,'r',encoding="utf-8").readlines()]
  return stopwords


def removeStopWords(sentence):
  stopwords = loadStopWords(config.data['path'] + config.data['stop_words'])
  output = ''
  sentence_seg = sentence.split(' ') # jieba.cut(sentence)
  for word in sentence_seg:
    if word not in stopwords and word != "":
      output += word
      output += " "
  return output


class Word2vecModel(object):
    def __init__(self, model=None, deterministic=False):
        self.model = None
        self.deterministic = deterministic
        if deterministic:
            random.seed(0)
        if model is not None:
            self.load_model(model)

    def load_model(self, model):
        self.model = gensim.models.word2vec.Word2Vec.load(model)
        return self

    def save_model(self, model):
        self.model.save(model)
        return self

    def train(self, data, c_data=None, vector_size=1000, window=15):
        clean_text_re = '[，。：？“”！、（）《》’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        fname = 'tmp_word2vec_data.txt'
        fout = open(fname, 'w', encoding='utf-8')
        for i, article in enumerate(data):
            line = re.sub(clean_text_re, ' ', article.strip())
            line_seg = removeStopWords(line)
            fout.write(line_seg)
            if (i % 1000 == 0):
              log("Saved " + str(i) + " documents")
        sentences = gensim.models.word2vec.Text8Corpus(fname)
        self.model = gensim.models.word2vec.Word2Vec(sentences, window=window, size=vector_size)
        os.remove(fname)
        return self

    def infer_vector(self, words, seed=0):
        if self.model is None:
            return None
        if self.deterministic:
            self.model.random.seed(seed) # Make the results deterministic for each prediction (obs: not over several runs)
        length = len(words)
        word_vecs = None
        for i in range(length):
            if i < len(words) and words[i] in self.model.wv:
                vecs = [self.model.wv[words[i]]]
            else:
                vecs = np.zeros([1, self.vector_size()]) # self.model.most_similar(word)[0]
            if word_vecs is None:
              word_vecs = np.array(vecs)
            else:
              word_vecs = np.append(word_vecs, vecs, axis=0)
        return word_vecs

    def vector_size(self):
        if self.model:
            return self.model.vector_size
        return None

