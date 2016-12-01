#!/bin/bash
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import numpy
import gensim
import bz2
import tensorflow_cluster as clusterAlgs

from PyTeaser.pyteaser import Summarize
from gensim_documents import manipulateArticle, Article, LabeledLineSentence, WikiCorpusDocuments, MMDBDocuments, MMDBDocumentLists
import numpy
from collections import Counter
import dotenv
dotenv.load()

def evaluate(article_offset=3000):
    centroid_file = open('trained-sources/centroids.txt', 'r')
    centroids = []
    categories = []
    for line in centroid_file:
        if len(categories) == 0:
            categories = line[:-1].split(';')
        elif len(centroids) == 0:
            centroids = [[float(number) for number in numbers.split(",")] for numbers in line.split('; ')]

    if len(centroids) == 0 or len(categories) == 0:
        return False

    # Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
    model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
    # data = MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category')
    data = MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles_EkonomiSport.csv')
    
    confusionMat = [[0 for c2 in categories] for c1 in categories]
    i = 0
    for i, (article, manart) in enumerate(data):
        if i < article_offset: # or i > 10000:
            continue
        # print article.content, article.category
        idx = doc2vecCategoriser(article.content, centroids)
        # print idx, categories, article.category
        if idx < 0 or idx >= len(categories):
            print "No category found"
            print idx, cidx, len(categories)
            continue

        category = article.category.lower().replace('&', 'o')
        if not category in categories:
            print "Unkown category detected"
            print category, categories
            continue
        cidx = categories.index(category)

        confusionMat[cidx][idx] += 1

    print '\t'.join(categories)
    for index, row in enumerate(confusionMat):
        print '\t'.join([str(num) for num in row]), '\t', categories[index]
    return True

model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
def doc2vecCategoriser(article, centroids):
    global model
    logger = logging.getLogger('doc2vec')

    # Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
    
    sumart = article # ' '.join(Summarize("", article, 5))
    artvec = model.infer_vector(manipulateArticle(sumart).split())
    artvec = numpy.array(artvec)
    max_similarity = -1000000
    idx = -1
    for index, centroid in enumerate(centroids):
        centroid = numpy.array(centroid)
        similarity = numpy.dot(centroid / numpy.linalg.norm(centroid), artvec / numpy.linalg.norm(artvec))
        # print "Sim: ", similarity
        if similarity > max_similarity:
            max_similarity = similarity
            idx = index
    # print idx, min_similarity
    return idx


# This function initiates the clustering with 
#   - articleCount as the maximum number of articles
#   - nrofclusters as the cluster count
#   - clusterOp as a callback function to manage each cluster content
def doc2vecCluster(articleCount = 3000, nrofclusters = 24, clusterOp = None):
    # Initiate the wiki corpus file to be read
    #data = WikiCorpusDocuments(bz2.BZ2File('../svwiki-latest-pages-articles.xml.bz2'))
    data = MMDBDocuments(dotenv.get('ARTICLE_PATH', '.') + '/articles_EkonomiSport.csv')
    # data = MMDBDocumentLists(dotenv.get('ARTICLE_PATH', '.') + '/csv_by_category')
    # Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
    model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))

    # This is where we store the articles to be feed in to the clustering algorithm
    articleVectors = []
    articles = []
    articleCategories = []
    
    # Get this global logger to print information about the process
    logger = logging.getLogger('doc2vec')


    # This is the count of articles we processed 
    c = 0
    logger.info("Start retrieve articles")
    # Retrieve the articles from the compressed file and in to memory (RAM)
    for (article, manArticle) in data:
        # If the maximum of articles we want is exceeded
        if c >= articleCount:
            break
        # Ignore articles that are too small or contains redirects to other articles
        #if len(article.content) < 100:
        #    continue

        # Comment if we want to cluster on the hole article
        summaries = Summarize(article.title, "".join(article.content))
        manArticle = ' '.join([manipulateArticle(summary) for summary in summaries])
        if manArticle == 'None':
            continue
                    
        # Calculate the doc2vec of the article manipulated version
        vector = model.infer_vector(doc_words=manArticle.split())
        vector = gensim.matutils.unitvec(vector)

        # Add the processed article vector into an array in RAM to do klustering on
        articleVectors.append(vector)
        #articles.append(article.content)
        articles.append(summaries)
        articleCategories.append(article.category.lower().replace('&', 'o'))
        c+=1 

    logger.info("Num of articles: %s " % len(articles))
    logger.info("Calc the clusters: ")

    # TFKMeansCluster - Is a k-means tensorflow clustering algorithm
    (centroids, assignments) = clusterAlgs.TFKMeansCluster(articleVectors, nrofclusters, 15)
    f = open('trained-sources/centroids.txt', 'w')
    categories = []
    for clusterIndex in range(nrofclusters):
        clusterArticles = [articleCategories[idx] for idx, assignment in enumerate(assignments) if assignment == clusterIndex]
        comons = Counter(clusterArticles).most_common(nrofclusters)
        for category in comons:
            if not category[0] in categories:
                categories.append(category[0])
                break
    f.write(';'.join(categories) + "\n")
    f.write('; '.join([','.join([str(number) for number in centroid]) for centroid in centroids]))
    f.close()
    if clusterOp is not None: 
        # retrieve the cluster result in an array
        #clusters = range(nrofclusters)

        for clusterIndex in range(nrofclusters):
            # Retrieve all article titles and contents for this cluster
            cluster = [Article(title='', category=articleCategories[idx], content=articles[idx], pageid=articleVectors[idx]) for idx, assignment in enumerate(assignments) if assignment == clusterIndex]
            #clusters[clusterIndex] = cluster

            # Use the callback to manage the cluster data
            clusterOp(cluster)

    # When finished we return the centroids that could be used to predict a new article inside one of these cluster
    return centroids

if __name__ == '__main__':
    # This function just prints the clusters title for an example
    idx = 0
    def handleCluster(cluster):
        return
        global idx
        # Initiate the doc2vec model to be used as the distance measurment in the cluster algorithm
        model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
        print "Cluster: ", idx
        articleStr = ''
        # art[0] = title, art[1] = content
        stats = {'Ekonomi': 0.0, 'Sport': 0.0}
        for article in cluster:
            stats[article.category] += 1.0
            articleStr += article.category + ", "

        for i in range(0, min(len(cluster), 20)):
            rightArt = cluster[i]
            mincloseness = 10000
            maxcloseness = -10000
            for j in range(i+1, len(cluster)):
                article = cluster[j]
                if rightArt and article.category != rightArt.category:
                    #print "First article is a " + rightArt[0] + " and contains:"
                    #print rightArt[1]
                    #print "Second article is a " + article[0] + " and contains:"
                    #print article[1]
                    #c = (sum([((article.vector[idx] - rightArt.vector[idx]) ** 2) for a in article.vector]) ** 0.5)
                    manArticle1 = ' '.join([manipulateArticle(content) for content in article.content])
                    manArticle2 = ' '.join([manipulateArticle(content) for content in rightArt.content])
                    
                    #c = numpy.dot(article.vector, rightArt.vector) 
                    c = model.docvecs.similarity_unseen_docs(model, manArticle1.split(), manArticle2.split())
                    if c < mincloseness:
                        mincloseness = c
                        minclosestArt = article
                    if c > maxcloseness:
                        maxcloseness = c
                        maxclosestArt = article
                    #rightArt = False
            if maxcloseness > -1000:
                print "Article 1 is of category " + rightArt.category
                print (" ".join(rightArt.content))
                print "----"
                print "The most similar article with oposite category; " + maxclosestArt.category
                print "has a similarity of: ", maxcloseness
                print (" ".join(maxclosestArt.content))
                print "|----------------------------------------------------------------------------------|"
                print " "
                #print "Similarity: ", mincloseness
                #print (" ".join(minclosestArt.content))
        #print articleStr
        #for i in stats:
        #    stats[i] = stats[i] / (float(len(cluster)))
        print stats
        idx += 1



    # start the clustering
    print "Training cluster algorithm"
    # centroids = doc2vecCluster(articleCount=2000, nrofclusters=2, clusterOp=lambda cluster: handleCluster(cluster))


    # Initiate the wiki corpus file to be read
    # data = WikiCorpusDocuments(bz2.BZ2File('wiki_sv/svwiki-latest-pages-articles.xml.bz2'), useLabeldTraining=False)
    
    print "Evaluating"
    evaluate(article_offset=2000)
    exit()
    # SPort article

    #model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
    
    lsi = gensim.models.lsimodel.LsiModel.load('wiki_sv/wiki_sv_lsi')
    tfidf = gensim.models.TfidfModel.load('wiki_sv/wiki_sv.tfidf_model')
    #dictionary = gensim.corpora.Dictionary.from_documents(data)
    #dictionary.save('wiki_sv/wiki_sv.dict')
    dictionary = gensim.corpora.Dictionary.load('wiki_sv/wiki_sv.dict')
    art1 = 'Marie Munters från Dala-Järna, bor sedan en tid tillbaka i Brasilien, där hon jobbar som beridare i en stor ridklubb.Marie, som representerar Vansbro Ryttarsällskap, tävlar också också i Sydamerika och nyligen nådde hon fina framgångar i en dressyrtävling.Med hästen Donfire S:t George slutade Marie 1:a i Intermediate freestyle och 2:a i Intermediate.Med hästen Crossy blev det en 2:a plats i Grand Prix freestyle och en 3:e plats i Grand Prix.'
    art2 = art1 #[5:]
    art_vec = dictionary.doc2bow(art1.split())
    art_vec = lsi[tfidf[art_vec]]
    print dictionary.get(art_vec.index(max(art_vec)), '::')
    print model.docvecs.similarity_unseen_docs(model, art1.split(), art2.split())

    #doc2vecCategoriser(first_article.content, centroids)