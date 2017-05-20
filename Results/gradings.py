#!/bin/bash
# -*- coding: utf-8 -*-


def readCSVLine(line, attr=None):
	l = line.strip()[1:-1].split('"§§"')
	if attr == None: return l
	return l[attr]

import sys
sys.path.append('../gensim')
import dotenv
dotenv.load()
import gensim
print dotenv.get('DOC2VEC_MODEL')
model = gensim.models.Doc2Vec.load(dotenv.get('DOC2VEC_MODEL'))
def similarity(s1, s2):
	global model
	return model.docvecs.similarity_unseen_docs(model, s1.split(), s2.split())

def fetchGrades():
	controlSentsPos = [278,202,152]
	controlSentsNeg = [292,126]
	# Positive
	# 278 Under det gångna året har många blivit lurade på pengar. Man tror att det kommer nya medel för att stoppa denna typ av brott -> Människor tror på vad som helst i _UNK.
	# 202 Butiken blev rånad på all potatis av en tjuv. -> Rånaren gick från butiken med potatis utan _UNK
	# 152 Antal brott i Gävle har ökat säger Stefan Karlsson. -> Mervärdet av antal brott i _UNK har ökat säger _UNK.

	# Negative
	# 292 Två bilar krockade med varandra i korsningen utanför Örnsköldsvik. -> Innan Börje Stenberg Leif Dessa svåra _UNK : Anders
	# 126 Han såg inte till särskilt boende på plattsen där han skadades för den 90-åriga Sundsvallskvinnan. -> En man i 00-årsåldern är misstänkt för snatteri på torsdagskvällen vid 00 . 00-tiden på lördagen.

	import collections
	import urllib2
	gradeCSV = urllib2.urlopen("http://projects.godesity.se/betygsattomskrivningar/data/classifies.txt").read().split('\n')
	sentenceOrig = urllib2.urlopen("http://projects.godesity.se/betygsattomskrivningar/data/sentence-orig.txt").read().split('\n')
	sentencePred = urllib2.urlopen("http://projects.godesity.se/betygsattomskrivningar/data/sentence-pred.txt").read().split('\n')
	headings = {attr: i for i, attr in enumerate(readCSVLine(gradeCSV[0]))}
	gradeCSV = gradeCSV[1:]
	uuids = [int(readCSVLine(line)[headings['uuid']]) for line in gradeCSV]
	grades = [[float(grade) 
					for i, grade in enumerate(readCSVLine(line, headings['class']).split(';')) if i < 3]
	 		 for line in gradeCSV]
	controlPosGrades = [lgrades for rowNr, lgrades in enumerate(grades) if uuids[rowNr]-1 in controlSentsPos]
	controlNegGrades = [lgrades for rowNr, lgrades in enumerate(grades) if uuids[rowNr]-1 in controlSentsNeg]
	validateGrades = [lgrades for rowNr, lgrades in enumerate(grades) if not (uuids[rowNr]-1 in controlSentsPos or uuids[rowNr]-1 in controlSentsNeg)]
	meanGrades = [sum(lgrades) / len(lgrades) for lgrades in validateGrades]

	validateGrades = [grade for lgrades in grades for grade in lgrades]
	countTree = collections.Counter(validateGrades)

	meanControlPosGrades = [sum(lgrades) / len(lgrades) for lgrades in controlPosGrades]
	meanControlNegGrades = [sum(lgrades) / len(lgrades) for lgrades in controlNegGrades]
	doc2vecGrades = [similarity(sentenceOrig[i], sentencePred[i]) for i, sent in enumerate(sentenceOrig)]
	return {
		'mean-validate-grades': meanGrades,
		'mean-control-pos-grades': meanControlPosGrades,
		'mean-control-neg-grades': meanControlNegGrades,
		'doc2vec-grades': doc2vecGrades,
		'count-tree': countTree,
		'mean': sum([sum(lgrades) for lgrades in grades]) / (3 * len(grades))
	}

if __name__ == '__main__':
	fetchGrades()