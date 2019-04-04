import gensim
import random
import re
from learning import config


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


class Doc2vecModel(object):
    def __init__(self, model=None, deterministic=False):
        self.model = None
        self.deterministic = deterministic
        if deterministic:
            random.seed(0)
        if model is not None:
            self.load_model(model)

    def load_model(self, model):
        self.model = gensim.models.Doc2Vec.load(model)
        return self

    def save_model(self, model):
        self.model.save(model)
        return self

    def train(self, data, c_data=None, epochs=10, vector_size=300, alpha=0.025):
        clean_text_re = '[，。：？“”！、（）《》’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        def to_labeled_sentence(data, c_data):
            for i, x in enumerate(data):
                x_only_words = re.sub(clean_text_re, ' ', x.strip())
                x_no_stop_words = removeStopWords(x_only_words)
                if c_data:
                    yield gensim.models.doc2vec.LabeledSentence(x_no_stop_words, c_data[i])
                else:
                    yield gensim.models.doc2vec.LabeledSentence(x_no_stop_words, [i])
        self.model = gensim.models.Doc2Vec(vector_size=vector_size,
                                           alpha=alpha,
                                           min_alpha=alpha,
                                           min_count=1,
                                           dm=1)
        self.model.build_vocab(to_labeled_sentence(data, c_data))
        for epoch in range(epochs):
            self.model.train(to_labeled_sentence(data, c_data),
                             total_examples=self.model.corpus_count,
                             epochs=self.model.iter)
            # decrease the learning rate
            self.model.alpha -= 0.002
            # fix the learning rate, no decay
            self.model.min_alpha = self.model.alpha
        return self

    def infer_vector(self, words, seed=0):
        if self.deterministic:
            self.model.random.seed(seed) # Make the results deterministic for each prediction (obs: not over several runs)
        return self.model.infer_vector(words)

    def vector_size(self):
        if self.model:
            return self.model.vector_size
        return None

