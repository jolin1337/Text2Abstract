
import gensim_documents
import random
import gensim.parsing.preprocessing as preprocessing
import gensim.matutils
import gensim.models
import sklearn.metrics
import numpy as np
from sklearn.svm import SVC

def process(doc):
  CUSTOM_FILTERS = [
    preprocessing.strip_tags,
    preprocessing.split_alphanum,
    preprocessing.strip_non_alphanum,
    preprocessing.strip_multiple_whitespaces,
    lambda d: d.lower(),
    lambda d: d.replace('!', '.'),
    lambda d: d.replace('?', '.')
  ]
  #print(' '.join(preprocessing.preprocess_string(doc, CUSTOM_FILTERS)))
  return ' '.join(preprocessing.preprocess_string(doc, CUSTOM_FILTERS))

def toVecs(content, model, word2vec=True):
  if word2vec:
    base_wordvec = model.wv['fotboll']
    # for word in content.replace('.', ' ').split():
    #   if word in model.wv:
    #     wv = model.wv[word]
    #   else:
    #     wv = np.zeros(len(base_wordvec))
    #   for num in wv:
    #     yield num
    words = content.replace('.', ' ').split()
    vecs = [model.wv[words[word_index]]
            if word_index < len(words) and words[word_index] in model.wv
            else np.zeros(len(base_wordvec))
            for word_index in range(100)]
    vecs = np.array(vecs).flatten()
    return vecs
  else:
    return gensim.matutils.unitvec(model.infer_vector(doc_words=content.split()))

def evalSvm(data, data_labels):
  model = SVC()
  split_point = int(len(data)/2)
  model.fit(data[:split_point], data_labels[:split_point])
  return model.score(data[split_point:], data_labels[split_point:])

def dot_product(doc1, doc2):
  return 4 - np.dot(doc1, doc2);

def main():
  # model = gensim.models.Doc2Vec.load("trained-sources/doc2vec_MM.model")
  model = gensim.models.Word2Vec.load("trained-sources/word2vec_MM_180521.model")
  data = gensim_documents.MMDBDocumentLists('../MM/csv_by_category/', useHeading=True, limit=-1)
  processed_data = [(toVecs(process(a.content), model, True), process(a.content), a.category) for a in data]
  random.shuffle(processed_data)
  docs, contents, labels = zip(*processed_data)

  categories = list(set(labels))
  labels = [categories.index(l) for l in labels]
  for i, category1 in enumerate(categories):
    for j, category2 in enumerate(categories):
      if i >= j: continue
      data = [d for di, d in enumerate(docs) if labels[di] == i or labels[di] == j]
      data_labels = [l for l in labels if l == i or l == j]
      print("Score between", category1, "and", category2, "=", evalSvm(data, data_labels))
  categories = [categories.index(c) for c in categories]

  #print(sklearn.metrics.silhouette_score(docs, labels, metric=dot_product))


if __name__ == '__main__':
  main()
