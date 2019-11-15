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


class CategorizerService:
    def __init__(self, category_level):
        self.model_file = config.model['path'] + \
            config.model['categorization_model_' + str(category_level)]['name']
        self.vec_model = VecModel(vec_file, deterministic=True)
        self.categorizer = Categorizer(self.vec_model, self.model_file)
        self.min_word_count = config.data.get('min_word_count', 10)

    def categorize_text(self, text):
        texts = [text]

        if len(striphtml(text).split()) < self.min_word_count:
            raise CategorizingArticleException(
                "Too few words in text to make a categorization", 400)

        prediction = self.categorizer.categorize_text(texts)
        return prediction
        

def categorize_text(text):
    predictions = {}
    for category_level in [1, 3, 4]:
        predictions[category_level] = CategorizerService(category_level).categorize_text(text)[0:7]

    category = None
    top_predictions = [predictions[level][0][0] for level in predictions]
    if top_predictions[0] in top_predictions[1] and top_predictions[1] in top_predictions[2]:
        category = top_predictions[2]

    return {
        'category': category,
        'predictions': [{ 'category_level': level, 'predictions': predictions[level] } for level in predictions]
        # 'classified_text': striphtml(text)
    }

if __name__ == '__main__':
    import pprint
    from sys import argv
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(categorize_text(argv[1]))
