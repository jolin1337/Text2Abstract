#!/bin/bash
# -*- coding: utf-8 -*-

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
	
	import urllib2
	gradeCSV = urllib2.urlopen("http://projects.godesity.se/betygsattomskrivningar/data/classifies.txt").read().split('\n')
	sentenceOrig = urllib2.urlopen("http://projects.godesity.se/betygsattomskrivningar/data/sentence-orig.txt").read().split('\n')
	headings = False
	countTree = dict()

	m = 0.0
	c = 0.0
	for rowNr, line in enumerate(gradeCSV):
		line = line.strip()[1:-1].split('"§§"')
		if not headings:
			headings = {attr: i for i, attr in enumerate(line)}
			continue
		id = line[headings['uuid']]
		grades = [float(grade) for i, grade in enumerate(line[headings['class']].split(';')) if i < 3]
		meanGrade = sum(grades) / len(grades)
		m += sum(grades)
		c += len(grades)

		currId = int(line[headings['uuid']])-1
		if currId in controlSentsPos:
			print 'Positive: ', grades, sentenceOrig[rowNr]
			continue

		if currId in controlSentsNeg:
			print 'Negative: ', grades, sentenceOrig[rowNr]
			continue

		for grade in grades:
			if grade in countTree:
				countTree[grade] += 1
			else: countTree[grade] = 1
		#if meanGrade in countTree: countTree[meanGrade] += 1
		#else: countTree[meanGrade] = 1

	print countTree
	print "TOTAL MEAN: ", m / c
	return {
		'count-tree': countTree,
		'mean': m / c
	}

if __name__ == '__main__':
	fetchGrades()