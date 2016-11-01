
#import gensim_documents as documents
import dotenv
dotenv.load()

__path__ = [dotenv.get('ARTICLE_PATH', '.')]
import extractSubjects
extractSubjects.extractArticlesWithCategories()
def trainCaterogry(category):
	pass