#!/bin/bash
# -*- coding: utf-8 -*-

import gensim
from os import listdir
import dotenv
dotenv.load()



# An article class to represent an article/document
class Article(object):
    def __init__(self, pageid, title, content, category=''):
        self.pageid = pageid
        self.title = title
        self.content = content
        self.category = category

#An cluster class to represent a group of articles belonging together with some pattern
class ArticleCluster(object):
    def __init__(self, id, articles):
        self.id = id
        self.articles = articles


class LabeledLineSentence(object):
    def __init__(self, filename):
        self.filename = filename
    def __iter__(self):
        for uid, line in enumerate(open(self.filename)):
            yield gensim.models.doc2vec.LabeledSentence(words=line.split(), tags=['SENT_%s' % uid])

class VectorDictionary(object):
    def __init__(self, model=gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))):
        # Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
        if isinstance(model, str) or isinstance(model, unicode):
            self.model = gensim.models.Doc2Vec.load(model)
        else:
            self.model = model
        self.X = []
        self.Y = []
        self.rawData = []
        self.labels = []
    def setModel(self, model):
        self.model = model
    def addToDictionary(self, article, pred=None):
        if isinstance(article, basestring):
            article = Article(content=article, category=pred)
        if not isinstance(article, Article) or article.content == 'None':
            return False
        if not article.category in self.labels:
            self.labels.append(article.category)
            self.labels.sort()
        artvec = self.model.infer_vector(doc_words=article.content.split())
        artvec = gensim.matutils.unitvec(artvec)
        # index = random.randrange(len(X)+1)
        self.rawData.append(article)
        self.X.append(artvec)
        self.Y.append(article.category)
        return True
    def clearDictionary(self):
        self.X = []
        self.Y = []
    def assignCopy(self, other):
        self.X = other.X
        self.Y = other.Y
        self.rawData = other.rawData
        self.labels = other.labels
        self.model = other.model

## The wiki corpus class that will manage the article contents and manipulate it for doc2vec
class WikiCorpusDocuments(object):
    # Init function when the object is created
    def __init__(self, corpusFile, limit=-1, useLabeldTraining=False):
        # Corpus is the file where the articles are stored
        self.corpus = corpusFile
        # Limit is the maximum number of articles to read if -1 all articles will be read
        self.limit = limit
        self.useLabeldTraining = useLabeldTraining

    #Iteration function which will be called from yield every iteration in an 
    # outer loop
    def __iter__(self):
        # Create an iterator for all articles in the file of self.corpus
        pages = gensim.corpora.wikicorpus.extract_pages(self.corpus)

        # ceep track on how many articles we have read already
        pageCount = 0

        #For each articles title, article content and article id
        for title, article, pageid in pages:
            # If we read enogh articles: abort
            if self.limit > -1 and self.limit <= pageCount:
                break

            # Remove Markup syntax and "tags" from the article content
            article = gensim.corpora.wikicorpus.remove_markup(article)
            # Remove ., !, ; etc. from the article so only the words are left
            doc = manipulateArticle(article)
            
            # Create a new article object based on the article and title
            articleObj = Article(pageid, title, article)


            pageCount += 1

            #Stop this loop here until next iteration
            if self.useLabeldTraining:
                yield gensim.models.doc2vec.LabeledSentence(words=doc.split(), tags=['SENT_%s' % pageid, title])
            else:
                yield article.split() #(articleObj, doc)
    

# Remove all non word characters
import re
manRegExp = re.compile('[^ \wåäöÅÄÖ]', re.UNICODE | re.IGNORECASE)
def manipulateArticle(doc):
    return manRegExp.sub(' ', doc).replace('  ', ' ')
    #unallowedChars = ["!", "*","(",")", "'", "\"", "=",":", ",", ".", ";", "-", "\n"]
    #for uc in unallowedChars:
    #    doc = doc.replace(uc, ' ')
    #doc = doc.replace('  ', ' ')
    #return doc

class MMDBDocuments(object):
    # Init function when the object is created
    def __init__(self, corpusCSVFile, limit=-1, useLabeldTraining=False, articleMod=lambda article: article, useHeading=False):
        self.corpus = corpusCSVFile
        self.limit = limit
        self.useLabeldTraining = useLabeldTraining
        self.articleMod = articleMod
        self.useHeading = useHeading

    def __iter__(self):
        pageCount = 0
        heading = {
            "uuid": 0,
            "title": 1,
            "body": 2,
            "category": 3
        }
        for (id, lineData) in enumerate(open(self.corpus)):
            # If we read enough articles: abort
            if self.limit > -1 and self.limit <= pageCount:
                break
            pageCount += 1

            articleData = lineData[1:-2].split('"§§"')
            if pageCount == 1 and self.useHeading:
                heading = {c: i for i, c in enumerate(articleData)}
                continue
            if len(articleData) != len(heading.values()):
                continue
            # Keep these lines for easier debuging of what column that is missing in csv file
            articleData[heading['title']]
            articleData[heading['body']]
            articleData[heading['category']]
            article = Article(id, articleData[heading['title']], articleData[heading['body']], articleData[heading['category']])
            if callable(self.articleMod):
                article = self.articleMod(article)

            if self.useLabeldTraining:
                yield gensim.models.doc2vec.LabeledSentence(words=article.content.split(), tags=[article.category])
            else:
                yield article

class MMDBDocumentLists(object):
    def __init__(self, dir, limit=-1, useLabeldTraining=False, articleMod=lambda article: article, useHeading=False):
        self.dir = dir
        self.limit = limit
        self.useLabeldTraining = useLabeldTraining
        self.articleMod = articleMod
        self.useHeading=useHeading
    def __iter__(self):
        files = [iter(MMDBDocuments(self.dir + '/' + f, self.limit, self.useLabeldTraining, self.articleMod, useHeading=self.useHeading)) for f in listdir(self.dir) if f.endswith('.csv')]
        i = -1
        file_count = len(files)
        while file_count > 0:
            i = (i+1) % file_count
            try:
                # print files, file_count
                yield files[i].next()

            except StopIteration as e:
                files.remove(files[i])
                i -= 1
                file_count -= 1
        raise StopIteration