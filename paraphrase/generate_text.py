#!/bin/bash
# -*- coding: utf-8 -*-

# TODO: Implement training for text generation
import sys
sys.path.append('../gensim')

import numpy as np
import dotenv
dotenv.load()

# A utility function to find the vertex with minimum dist value, from
# the set of vertices still in queue
def minDistance(dist,queue):
	# Initialize min value and min_index as -1
	minimum = float("Inf")
	min_index = -1
	#from the dist array,pick one which has min value and is till in queue
	for i in range(len(dist)):
		if dist[i] < minimum and i in queue:
			minimum = dist[i]
			min_index = i
	return min_index
def dijkstra(graph, src):

	row = len(graph)
	col = len(graph[0])

	# The output array. dist[i] will hold the shortest distance from src to i
	# Initialize all distances as INFINITE 
	dist = [float("Inf")] * row

	#Parent array to store shortest path tree
	parent = [-1] * row

	# Distance of source vertex from itself is always 0
	dist[src] = 0
 
	# Add all vertices in queue
	queue = []
	for i in range(row):
		queue.append(i)
		 
	#Find shortest path for all vertices
	while queue:

		# Pick the minimum dist vertex from the set of vertices
		# still in queue
		u = minDistance(dist, queue)    
		if u < 0:
			break
		# remove min element    
		queue.remove(u)

		# Update dist value and parent index of the adjacent vertices of
		# the picked vertex. Consider only those vertices which are still in
		# queue
		for i in range(col):
			'''Update dist[i] only if it is in queue, there is
			an edge from u to i, and total weight of path from
			src to i through u is smaller than current value of
			dist[i]'''
			if graph[u][i] and i in queue:
				if dist[u] + graph[u][i] < dist[i]:
					dist[i] = dist[u] + graph[u][i]
					parent[i] = u
	return dist, parent

def getAdjacencyMatrix(wordEdges, wordCount):
	print "converting sentences to word matrix"
	edgeMatrix = np.zeros((wordCount, wordCount), dtype=np.int64)
	for i in range(wordCount):
		for sentence in wordEdges:
			if not i in sentence: continue
			l = len(sentence)
			for index, word in enumerate(sentence):
				# if index <= 0 or index >= l-1 continue
				if sentence[index] == i:
					if index < l-1: edgeMatrix[i][sentence[index+1]] += 1
					if index > 0: edgeMatrix[sentence[index-1]][i] += 1
	return edgeMatrix

## Try to see similarities between title and text for text generation
from PyTeaser.pyteaser import Summarize
for i, lin in enumerate(open(dotenv.get('ARTICLE_PATH', './') + 'tmp-articles-dump_april_16_1205-filter-uuid')):
	if i == 0:
		print lin
	if i >= 10:
		attrs = lin[1:-2].split('"§§"')
		text = attrs[0]
		print "Summary: ", ' '.join(Summarize('', text, 3))
		print "Lead: ", attrs[-2]
		print "Title", attrs[-1],
		break
exit()


## An poor atempt for collecting the relations between existing words and their classes and generate a sentence out of it
import sklearn
import posextractor

pos = posextractor.readPOSFromConll('../MM/pos_by_category/articles_MM_Allmänt.conll', 100)
dictionary    = {}
invDictionary    = {}
dictionaryFrq = {}
wordEdges = []
wordCount = 0

for index, taggs in enumerate(pos):
	if index == 0: continue
	edgeList = []
	for tagg in taggs:
		if tagg.word in dictionary:
			dictionaryFrq[tagg.word] += 1
		else:
			dictionaryFrq[tagg.word] = 1
			dictionary[tagg.word] = wordCount
			invDictionary[wordCount] = tagg.word
			wordCount += 1
		edgeList.append(dictionary[tagg.word])
	wordEdges.append(edgeList)
	# root = taggs[[tagg.parent == "0" for tagg in taggs].index(True)]
	# print "Root: ", root.word, root.tagg
	# print '\n'.join(['\t'.join(tagg.conll) for tagg in taggs])
	# print ' '.join([tagg.word + ' (' + tagg.tagg + ')' for tagg in taggs])
	# print ', '.join([tagg.word for tagg in taggs if tagg.tagg in ['AB', 'VB']])
	# print ', '.join([tagg.word for tagg in taggs if tagg.tagg in ['NN']])
	# print ''

for tagg in pos[0]:
	if not tagg.word in dictionary:
		dictionary[tagg.word] = wordCount
		wordCount += 1
wordEdges.append([dictionary[tagg.word] for tagg in pos[0]])
edgeMatrix = getAdjacencyMatrix(wordEdges, wordCount)
newsentence = [dictionary[tagg.word] for tagg in pos[0] if tagg.tagg in ['NN', 'AB', 'VB']]
index = 0
l = len(newsentence)
while index < l-1:
	dist, words = dijkstra(edgeMatrix, newsentence[index])
	word = words[newsentence[index+1]]
	j = 1
	while word != -1:
		newsentence.insert(index+j, word)
		word = words[word]
		j += 1
print len(edgeMatrix), ' '.join([invDictionary[word] for word in newsentence])
# coords = sklearn.manifold.locally_linear_embedding(edges, 3, 3)