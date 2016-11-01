#!/bin/bash
# -*- coding: utf-8 -*-

from pyteaser import Summarize
url = 'http://www.huffingtonpost.com/2013/11/22/twitter-forward-secrecy_n_4326599.html'
title = "Regeringen vill kartlägga svenskarnas sexvanor"
article = "Studiens fokus ska vara på sexuell och reproduktiv hälsa och rättigheter som en hälsofaktor ur ett folkhälso- och jämlikhetsperspektiv. Hänsyn ska tas till bland annat ålder och funktionsnedsättning. Studien ska även belysa förekomsten av sexuellt- och annat våld och dess konsekvenser för sexuell och reproduktiv hälsa och rättigheter. Studien ska kartlägga grundläggande skillnader och utvecklingen rörande sexuell och reproduktiv hälsa och lyfta vilka områden och grupper som behöver hälsofrämjande insatser. Studien ska genomföras i samråd med relevanta myndigheter, högskolor och universitet samt berörda förbund och organisationer i det civila samhället, däribland RFSU och RFSL. Resultaten från studien kommer redovisas på regional nivå och om möjligt på kommunal nivå."
summaries = Summarize(title, article)

wordCount = 0
for summary in summaries:
	print summary
	wordCount += len(summary.split())
	print "-----"

print "Words in original article: ", len(article.split()) + len(title.split())
print "Words in summary: ", wordCount