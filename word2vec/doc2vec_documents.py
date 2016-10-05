#!/bin/bash
# -*- coding: utf-8 -*-

import gensim


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
                yield (articleObj, doc)
    

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
    def __init__(self, corpusCSVFile, limit=-1, useLabeldTraining=False):
        self.corpus = corpusCSVFile
        self.limit = limit
        self.useLabeldTraining = useLabeldTraining

    def __iter__(self):
        pageCount = 0
        for (id, lineData) in enumerate(open(self.corpus)):
            # If we read enogh articles: abort
            if self.limit > -1 and self.limit <= pageCount:
                break

            pageCount += 1

            articleData = lineData.split('§§', 4)
            articleTitle = articleData[1][1:-1]
            articleContent = articleData[2][1:-1]
            articleCategory = articleData[3][1:-2]
            article = Article(id, articleTitle, articleContent, articleCategory)

            if self.useLabeldTraining:
                yield gensim.models.doc2vec.LabeledSentence(words=manipulateArticle(articleContent).split(), tags=[articleCategory])
            else:
                yield (article, manipulateArticle(articleContent))

