import unittest
from model import filter_article_category_lengths
from web.app import categorize_text
from learning.categorizer_model import Categorizer
from learning.word2vec_model import Word2vecModel
from learning.doc2vec_model import Doc2vecModel
from learning import config
if config.model['vec_model']['type'] == 'doc2vec':
    VecModel = Doc2vecModel
else:
    VecModel = Word2vecModel
vec_file = config.model['path'] + config.model['vec_model']['name']
model_file = config.model['path'] + \
    config.model['categorization_model']['name']
vec_model = VecModel(vec_file, deterministic=True)
categorizer = Categorizer(vec_model, model_file)


class TestModel(unittest.TestCase):
    def test_filter_article_category_lengths(self):
        articles = [
            ('text', ['RYF-BIZ-WZJ-GNO-BUL']),
            ('text', ['RYF-BIZ-WZJ'])
        ]
        expected = [
            ('text', ['RYF-BIZ-WZJ'])
        ]
        self.assertEqual(list(filter_article_category_lengths(articles, 11)), expected)

    def test_categorize_text(self):
        text = 'Populära rallytävlingen ställs in: "Finns ingen is på vägarna" Årets upplaga av LBC-ruschen skulle ha körts nu på lördag, den nionde mars. Men för ungefär en vecka sedan tog arrangören ett beslut om att ställa in tävlingen. – Tövädret har gjort att det inte finns någon is på vägarna, säger Ann-Christin Renhall. LBC-ruschen är en av landets populäraste rallytävlingar och i år fanns 179 ekipage anmälda. Har ni fått några rektioner från de anmälda förarna? – Ja, alla tycker förstås att det är väldigt tråkigt. Samtidigt har de stor förståelse för vårt beslut och att vi dessutom tog det ganska tidigt. Prognosen såg inte särskilt lovande ut och det hade kostat oss för mycket pengar att ställa in tävlingen i ett senare skede, säger Renhall som lovar att Lima MS kommer igen nästa år. – Vi hoppas på bättre förhållanden då.'
        result = categorizer.categorize_text([text])[0]
        self.assertEqual(result[0], 'RYF-QPR-HGB-DNB')
        self.assertGreater(result[1], 0.7)


if __name__ == '__main__':
    unittest.main()
