from learning.word2vec_model import Word2vecModel
from learning.doc2vec_model import Doc2vecModel
from learning.categorizer_model import Categorizer
from learning import config
from learning.utils import striphtml

if config.model['vec_model']['type'] == 'doc2vec':
    VecModel = Doc2vecModel
else:
    VecModel = Word2vecModel
vec_file = config.model['path'] + config.model['vec_model']['name']


class AppException(Exception):
    def __init__(self, message, status_code):
        super(AppException, self).__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {
            'message': self.message
        }


class CategorizingArticleException(AppException):
    def __init__(self, *argv, **argd):
        super().__init__(*argv, **argd)

    def to_dict(self):
        return {
            **super().to_dict(),
            "error": "Categorizing article"
        }


def categorize_text(text, category_level):
    model_file = config.model['path'] + \
        config.model['categorization_model_' + str(category_level)]['name']


    vec_model = VecModel(vec_file, deterministic=True)
    categorizer = Categorizer(vec_model, model_file)
    min_word_count = config.data.get('min_word_count', 10)

    texts = [text]
    entities = []

    if len(striphtml(text).split()) < min_word_count:
        raise CategorizingArticleException(
            "Too few words in text to make a categorization", 400)

    prediction = categorizer.categorize_text(texts)
    categories = [{'category_name': c, 'category_probability': p}
                  for c, p in prediction]
    categories.sort(key=lambda c: c['category_name'])
    category = max(categories, key=lambda c: c['category_probability'])
    return {
        'category': category,
        'categories': prediction,
        'entities': [{
            'tag': ent.tag,
            'words': ent,
            'start_word_index': ent.start,
            'end_word_index': ent.end
        } for ent in entities],
        'classified_text': striphtml(text)
    }
