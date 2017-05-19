#!/bin/bash
# -*- coding: utf-8 -*-
import sys
sys.path.append('../gensim')
import dotenv
dotenv.load()

from PyTeaser.pyteaser import Summarize
import re
sentencePattern = re.compile(r'[\\.\\!\\?;\n]')
wordPattern = re.compile(r'[^\wåäöÅÄÖ]*')

def makeParagraph(text):
  return '<p>' + '</p><p>'.join(text.split('\n')) + '</p>'
def makeSentence(text):
  return '<s> ' + ' . </s><s> '.join(sentencePattern.split(text)) + ' </s>'

def iter_mm_documents():
  # dataSource = dotenv.get('ARTICLE_PATH', '.') + '/articles.csv'
  dataSource = dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_april_14_1723-filter-uuid'
  headings = False
  for i, line in enumerate(open(dataSource, 'r')):
    # if i >= 70000:
    #   break
    attrs = line[1:-2].split('"§§"')
    if headings == False:
      headings = {attr: index for index, attr in enumerate(attrs)}
      continue
    if 'u\'Allm' in attrs[headings['category']]:
      yield headings, attrs

def texsum_convert_vocab():
  with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/texsum.vocab', 'w') as texsumFile:
    words = {}
    for headings, attrs in iter_mm_documents():
      article = attrs[headings['body']]
      for word in wordPattern.split(article):
        if word == "":
          continue
        word = word.lower()
        if word in words:
          words[word] += 1
        else:
          words[word] = 1
    for word in sorted(words, key=lambda item: words[item]):
      texsumFile.write('%s %s\n' % (word, words[word]))

def texsum_convert():
  texsum_convert_vocab()
  with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/texsum.txt', 'w') as texsumFile:
    for headings, attrs in iter_mm_documents():
        article = attrs[headings["body"]]
        abstract = ' '.join(Summarize(attrs[headings["title"]], attrs[headings["body"]], 3))
        texsumFile.write('abstract=<d>' + makeParagraph(makeSentence(abstract)) + '</d>\t' +
                         'article=<d>' + makeParagraph(makeSentence(article)) + '</d>\tpublisher=Mittmedia\n')
def translate_convert():
  with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/body-language.sv', 'w') as bodyFile:
    with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/summary-language.sv', 'w') as summaryFile:
      with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/lead-language.sv', 'w') as leadFile:
        with open(dotenv.get('PARAPHRASE_MODEL', '.') + '/title-language.sv', 'w') as titleFile:
          for headings, attrs in iter_mm_documents():
            title = attrs[headings["title"]]
            lead = attrs[headings["lead"]]
            body = attrs[headings["body"]]
            summary = ' '.join(Summarize(attrs[headings["title"]], attrs[headings["body"]], 1))
            # article = attrs[headings["title"]]
            # abstract = attrs[headings["body"]]

            (title, lead, body, summary) = ('. '.join(re.split(u'\n|\n|\r', text, flags=re.UNICODE))
                  for text in [title, lead, body, summary])

            bodyFile.write(body + '\n\n')
            summaryFile.write(summary + '\n\n')
            leadFile.write(lead + '\n\n')
            titleFile.write(title + '\n\n')

if __name__ == '__main__':
  translate_convert()
  # texsum_convert()