import re
from keras import backend as K
import html

body_pattern = re.compile(r'<([^p\/]).*?>.*?<\/\1.*?>')
html_pattern = re.compile(r'<.*?>')
meta_pattern = re.compile(r'\[.*?\]')
dspaces_pattern = re.compile(r' +')
def striphtml(data):
  body_cleared = body_pattern.sub(' ', data)
  html_cleared = html_pattern.sub(' ', body_cleared)
  unescaped = html.unescape(html_cleared)
  meta_cleared = meta_pattern.sub(' ', unescaped)
  dspaces_cleared = dspaces_pattern.sub(' ', meta_cleared)
  return dspaces_cleared.strip()


def split_train_validation_data(split, x_data, y_data):
  limit_train  = (int)(len(x_data) * split)
  return x_data[:limit_train], y_data[:limit_train], \
         x_data[limit_train:], y_data[limit_train:]


def offset_binary_accuracy(y_true, y_pred, offset=0.2):
    return K.mean(K.equal(y_true, K.round(K.max([1.0] * y_pred.shape[-1], y_pred))), axis=-1)

def f1_score(y_true, y_pred):
    def recall(y_true, y_pred):
        """Recall metric.

        Only computes a batch-wise average of recall.

        Computes the recall, a metric for multi-label classification of
        how many relevant items are selected.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
        recall = true_positives / (possible_positives + K.epsilon())
        return recall

    def precision(y_true, y_pred):
        """Precision metric.

        Only computes a batch-wise average of precision.

        Computes the precision, a metric for multi-label classification of
        how many selected items are relevant.
        """
        true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
        predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
        precision = true_positives / (predicted_positives + K.epsilon())
        return precision
    precision = precision(y_true, y_pred)
    recall = recall(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))
