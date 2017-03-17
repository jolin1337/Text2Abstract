#!/bin/bash
# -*- coding: utf-8 -*-

import subprocess
import dotenv
dotenv.load()

class Tagg(object):
	def __init__(self, conllLine):
		self.conll = conllLine
		self.id = conllLine[0]
		self.word = conllLine[1]
		self.tagg = conllLine[3]
		self.parent = conllLine[6]

class POSTagger(object):
	def __init__(self, str):
		pass
def POSParse(str, sep="\t"):
	docs = []
	taggs = []
	
	for i, posLine in enumerate(str.split("\n")):
		posLine = posLine.split(sep, 7)
		if len(posLine) < 7: # End of document
			if len(taggs) > 0:
				docs.append(taggs)
				taggs = []
			continue
		taggs.append(Tagg(posLine))

	for taggs in docs:
		taggsSorted = sorted(taggs, key=lambda tagg: tagg.parent)
		root = None
		for tagg in taggsSorted:
			if tagg.parent != "0":
				tagg.parent = taggs[int(tagg.parent)-1]
			else:
				root = tagg
	return (POSTagger(""), docs)

def posSentences(sentences, parse=True):
	return posSentence(sentences, parse)
	
def posSentence(sentences, parse=True):
	if not isinstance(sentences, list):
		sentences = [sentences]
	try:
		# print ('cd ' + dotenv.get('PARSER_DIRECTORY', './') + 
		# 	' && echo "' + '\n'.join([sentence.replace("\n", " ").replace('\'', ' ') for sentence in sentences]) + 
		# 	'" | ' + dotenv.get('PARSER_CMD', '.'))
		pos = subprocess.check_output(
			'cd ' + dotenv.get('PARSER_DIRECTORY', './') + 
			' && echo \'' + '\n'.join([sentence.replace("\n", " ").replace('\'', ' ') for sentence in sentences]) + 
			'\' | ' + dotenv.get('PARSER_CMD', '.'), shell=True)
	except Exception as e:
		return None
	if parse:
		tagger, docs = POSParse(pos)
		return docs
	else:
		return pos

def readPOSFromConll(fileName, max_pos=0):
	posContent = ''
	poses = []
	for line in open(fileName):
		line = line[:-1]
		if line == '' and posContent != '':
			tagger, docs = POSParse(posContent)
			if len(docs) > 0:
				poses.append(docs[0])
				if max_pos != 0 and len(poses) >= max_pos:
					break
			posContent = ''
		else:
			posContent += line + "\n"
	return poses

from gensim_documents import manipulateArticle
def extractPOSArticlesWithCategories(categories=[]):
	cats = []
	files = []
	lenCategories = len(categories)
	for line in open(dotenv.get('ARTICLE_PATH', '.') + '/articles.csv'):
		articleData = [col[1:-2] for col in line.split('§§')]

		# The article content itself
		pos = posSentence([manipulateArticle(data) for data in articleData[2].split(".")], False)
		if pos == None:
			continue
		cat = articleData[len(articleData)-1]

		if lenCategories > 0 or cat in categories:
			if cat in cats:
				f = files[cats.index(cat)]
			else:
				f = open(dotenv.get('ARTICLE_PATH', '.') + '/articles_MM_' + cat + ".conll", 'w')
				files.append(f)
				cats.append(cat)
			f.write(pos)
			f.write("\n")

	for f in files:
		f.close()

if __name__ == '__main__':
	extractPOSArticlesWithCategories()	
	#print posSentence(["Jag spelar \nfotboll", "Jag är fin"], False)