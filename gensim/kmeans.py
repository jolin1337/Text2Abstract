import doc2vec_clustering as clust
import sys
text = ''.join(sys.stdin)
categories = clust.categoriseText(text, open(sys.argv[1], 'r'))

for category, probability in categories.iteritems():
	print '__label__' + category, probability