import unittest
from model import filter_article_category_lengths
from web.categorizer_service import categorize_text
from learning.categorizer_model import Categorizer
from learning.word2vec_model import Word2vecModel
from learning.doc2vec_model import Doc2vecModel
from learning import config
if config.model['vec_model']['type'] == 'doc2vec':
    VecModel = Doc2vecModel
else:
    VecModel = Word2vecModel
vec_file = config.model['path'] + config.model['vec_model']['name']
vec_model = VecModel(vec_file, deterministic=True)

model_file_1 = config.model['path'] + \
    config.model['categorization_model_1']['name']
categorizer_1 = Categorizer(vec_model, model_file_1)
model_file_3 = config.model['path'] + \
    config.model['categorization_model_3']['name']
categorizer_3 = Categorizer(vec_model, model_file_3)
model_file_4 = config.model['path'] + \
    config.model['categorization_model_4']['name']
categorizer_4 = Categorizer(vec_model, model_file_4)


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

    def test_categorize_text_level_1(self):
        text = 'Gustaf Berglund, som tävlar för IFK Mora, hade tillsammans med Johan Häggström lyckats ta sig till finalen i söndagens sprintstafett, när det andra svenska laget med Gustav Nordström och Teodor Peterson hade åkt ut redan i prologen. I finalen låg Sverige bra med i klungan, men då körde Gustaf Berglund ihop med ryske Artiom Maltsev och föll. – Han var på min skida litegrann. Det var därför jag ramlade. Jag vet inte exakt vad som hände. Inombords är jag kanske lite mer upprörd än vad jag är utåt, säger Berglund till . Men trots det så lyckades Johan Häggström komma ikapp klungan igen, och Sverige slutade på en åttondeplats. De svenska herrarna hyllades för sin placering, och Berglund var nöjd med helgens instatser. – Jag är helt makalöst glad över att ha fått chansen att åka här och att det har gått så bra som det faktiskt har gjort. Det gav verkligen mersmak, säger Gustaf Berglund till . Nästa vecka är det dags för U23-VM där Berglund ska delta, och när han under dagens lopp sträckte höften är han orolig för hur det ska påverka. – Jag är lite orolig. Jag vill verkligen vara bra till dess. Jag ska verkligen försöka få till det, säger han till . U23-VM hålls i Lahti mellan den 20 och 27 januari'
        result = categorizer_1.categorize_text([text])[0]
        self.assertEqual(result[0][0], 'RYF-QPR')
        self.assertGreater(result[0][1], 0.7)

    def test_categorize_text_level_3(self):
        text = 'Gustaf Berglund, som tävlar för IFK Mora, hade tillsammans med Johan Häggström lyckats ta sig till finalen i söndagens sprintstafett, när det andra svenska laget med Gustav Nordström och Teodor Peterson hade åkt ut redan i prologen. I finalen låg Sverige bra med i klungan, men då körde Gustaf Berglund ihop med ryske Artiom Maltsev och föll. – Han var på min skida litegrann. Det var därför jag ramlade. Jag vet inte exakt vad som hände. Inombords är jag kanske lite mer upprörd än vad jag är utåt, säger Berglund till . Men trots det så lyckades Johan Häggström komma ikapp klungan igen, och Sverige slutade på en åttondeplats. De svenska herrarna hyllades för sin placering, och Berglund var nöjd med helgens instatser. – Jag är helt makalöst glad över att ha fått chansen att åka här och att det har gått så bra som det faktiskt har gjort. Det gav verkligen mersmak, säger Gustaf Berglund till . Nästa vecka är det dags för U23-VM där Berglund ska delta, och när han under dagens lopp sträckte höften är han orolig för hur det ska påverka. – Jag är lite orolig. Jag vill verkligen vara bra till dess. Jag ska verkligen försöka få till det, säger han till . U23-VM hålls i Lahti mellan den 20 och 27 januari'
        result = categorizer_3.categorize_text([text])[0]
        self.assertEqual(result[0][0], 'RYF-QPR-HGB-AYA')
        self.assertGreater(result[0][1], 0.7)

    def test_categorize_text_level_4(self):
        text = 'Gustaf Berglund, som tävlar för IFK Mora, hade tillsammans med Johan Häggström lyckats ta sig till finalen i söndagens sprintstafett, när det andra svenska laget med Gustav Nordström och Teodor Peterson hade åkt ut redan i prologen. I finalen låg Sverige bra med i klungan, men då körde Gustaf Berglund ihop med ryske Artiom Maltsev och föll. – Han var på min skida litegrann. Det var därför jag ramlade. Jag vet inte exakt vad som hände. Inombords är jag kanske lite mer upprörd än vad jag är utåt, säger Berglund till . Men trots det så lyckades Johan Häggström komma ikapp klungan igen, och Sverige slutade på en åttondeplats. De svenska herrarna hyllades för sin placering, och Berglund var nöjd med helgens instatser. – Jag är helt makalöst glad över att ha fått chansen att åka här och att det har gått så bra som det faktiskt har gjort. Det gav verkligen mersmak, säger Gustaf Berglund till . Nästa vecka är det dags för U23-VM där Berglund ska delta, och när han under dagens lopp sträckte höften är han orolig för hur det ska påverka. – Jag är lite orolig. Jag vill verkligen vara bra till dess. Jag ska verkligen försöka få till det, säger han till . U23-VM hålls i Lahti mellan den 20 och 27 januari'
        result = categorizer_4.categorize_text([text])[0]
        # ["RYF-QPR-HGB", "RYF-QPR", "RYF-QPR-HGB-AYA-MFT", "RYF-QPR-HGB-AYA"]
        self.assertEqual(result[0][0], 'RYF-QPR-HGB-AYA-MFT')
        self.assertGreater(result[0][1], 0.9)

    def test_categorize_text(self):
        text = 'Gustaf Berglund, som tävlar för IFK Mora, hade tillsammans med Johan Häggström lyckats ta sig till finalen i söndagens sprintstafett, när det andra svenska laget med Gustav Nordström och Teodor Peterson hade åkt ut redan i prologen. I finalen låg Sverige bra med i klungan, men då körde Gustaf Berglund ihop med ryske Artiom Maltsev och föll. – Han var på min skida litegrann. Det var därför jag ramlade. Jag vet inte exakt vad som hände. Inombords är jag kanske lite mer upprörd än vad jag är utåt, säger Berglund till . Men trots det så lyckades Johan Häggström komma ikapp klungan igen, och Sverige slutade på en åttondeplats. De svenska herrarna hyllades för sin placering, och Berglund var nöjd med helgens instatser. – Jag är helt makalöst glad över att ha fått chansen att åka här och att det har gått så bra som det faktiskt har gjort. Det gav verkligen mersmak, säger Gustaf Berglund till . Nästa vecka är det dags för U23-VM där Berglund ska delta, och när han under dagens lopp sträckte höften är han orolig för hur det ska påverka. – Jag är lite orolig. Jag vill verkligen vara bra till dess. Jag ska verkligen försöka få till det, säger han till . U23-VM hålls i Lahti mellan den 20 och 27 januari'
        category = categorize_text(text)['category']
        # ["RYF-QPR-HGB", "RYF-QPR", "RYF-QPR-HGB-AYA-MFT", "RYF-QPR-HGB-AYA"]
        self.assertEqual(category, 'RYF-QPR-HGB-AYA-MFT')


if __name__ == '__main__':
    unittest.main()
