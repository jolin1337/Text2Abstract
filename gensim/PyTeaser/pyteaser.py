#!/bin/bash
# -*- coding: utf-8 -*-

from collections import Counter
from math import fabs
from re import split as regex_split, sub as regex_sub, UNICODE as REGEX_UNICODE

stopWords = set([
    "-", " ", ",", ".", 
    "kunna", "om", "ovan", "enligt", "i enlighet med detta", "över", "faktiskt", "efter", "efteråt", "igen", "mot", "är inte", "alla", "tillåta", "tillåter", "nästan", "ensam", "längs", "redan", "också", "även om", "alltid", "am", "bland", "bland", "en", "och", "en annan", "någon", "någon", "hur som helst", "någon", "något", "ändå", "ändå", "var som helst", "isär", "visas", "uppskatta", "lämpligt", "är", "inte", "runt", "som", "åt sidan", "be", "frågar", "associerad", "vid", "tillgängliga", "bort", "väldigt", "vara", "blev", "eftersom", "bli", "blir", "blir", "varit", "innan", "förhand", "bakom", "vara", "tro", "nedan", "bredvid", "förutom", "bäst", "bättre", "mellan", "bortom", "både", "kort", "men", "genom", "c", "c'mon", "c: s", "kom", "kampanj", "kan", "kan inte", "kan inte", "cant", "orsaka", "orsaker", "viss", "säkerligen", "förändringar", "klart", "co", "com", "komma", "kommer", "om", "följaktligen", "överväga", "överväger", "innehålla", "innehållande", "innehåller", "motsvarande", "kunde", "kunde inte", "kurs", "närvarande", "definitivt", "beskrivits", "trots", "gjorde", "inte", "olika", "göra", "gör", "inte", "gör", "inte", "gjort", "ned", "nedåt", "under", "varje", "edu", "åtta", "antingen", "annars", "någon annanstans", "tillräckligt", "godkändes", "helt", "speciellt", "et", "etc", "även", "någonsin", "varje", "alla", "alla", "allt", "överallt", "ex", "exakt", "exempel", "utom", "långt", "få", "femte", "först", "finansiella", "fem", "följt", "efter", "följer", "för", "fd", "tidigare", "framåt", "fyra", "från", "ytterligare", "dessutom", "få", "blir", "få", "given", "ger", "gå", "går", "gå", "borta", "fick", "fått", "hälsningar", "hade", "hade inte", "händer", "knappast", "har", "har inte", "ha", "har inte", "med", "han", "han är", "hallå", "hjälpa", "hence", "henne", "här", "här finns", "härefter", "härmed", "häri", "härpå", "hennes", "själv", "hej", "honom", "själv", "hans", "hit", "förhoppningsvis", "hur", "howbeit", "dock", "jag skulle", "jag ska", "jag är", "jag har", "om", "ignoreras", "omedelbar", "i", "eftersom", "inc", "indeed", "indikera", "indikerade", "indikerar", "inre", "mån", "istället", "in", "inåt", "är", "är inte", "den", "det skulle", "det ska", "det är", "dess", "själv", "bara", "hålla", "håller", "hålls", "vet", "vet", "känd", "sista", "nyligen", "senare", "senare", "latterly", "minst", "mindre", "lest", "låt", "låt oss", "liknande", "gillade", "sannolikt", "lite", "ser", "ser", "ser", "ltd", "huvudsakligen", "många", "kan", "kanske", "mig", "betyda", "under tiden", "endast", "kanske", "mer", "dessutom", "mest", "mestadels", "mycket", "måste", "min", "själv", "namn", "nämligen", "nd", "nära", "nästan", "nödvändigt", "behöver", "behov", "varken", "aldrig", "ändå", "ny", "nästa", "nio", "ingen", "ingen", "icke", "ingen", "ingen", "eller", "normalt", "inte", "ingenting", "roman", "nu", "ingenstans", "uppenbarligen", "av", "off", "ofta", "oh", "ok", "okay", "gammal", "på", "en gång", "ett", "ettor", "endast", "på", "eller", "andra", "andra", "annars", "borde", "vår", "vårt", "oss", "ut", "utanför", "över", "övergripande", "egen", "särskilt", "särskilt", "per", "kanske", "placeras", "vänligen", "plus", "möjligt", "förmodligen", "förmodligen", "ger", "ganska", "citera", "kvartalsvis", "snarare", "verkligen", "rimligen", "om", "oavsett", "gäller", "relativt", "respektive", "höger", "sa", "samma", "såg", "säga", "säger", "säger", "andra", "det andra", "se", "ser", "verkar", "verkade", "informationsproblem", "verkar", "sett", "själv", "själva", "förnuftig", "skickas", "allvarlig", "allvarligt", "sju", "flera", "skall", "hon", "bör", "bör inte", "eftersom", "sex", "så", "några", "någon", "på något sätt", "någon", "något", "sometime", "ibland", "något", "någonstans", "snart", "sorry", "specificerade", "ange", "ange", "fortfarande", "sub", "sådan", "sup", "säker", "t s", "ta", "tas", "berätta", "tenderar", "än", "tacka", "tack", "thanx", "att", "det är", "brinner", "den", "deras", "deras", "dem", "själva", "sedan", "därifrån", "där", "det finns", "därefter", "därigenom", "därför", "däri", "theres", "därpå", "dessa", "de", "de hade", "de kommer", "de är", "de har", "tror", "tredje", "detta", "grundlig", "grundligt", "de", "though", "tre", "genom", "hela", "thru", "sålunda", "till", "tillsammans", "alltför", "tog", "mot", "mot", "försökte", "försöker", "verkligt", "försök", "försöker", "två gånger", "två", "enligt", "tyvärr", "såvida inte", "osannolikt", "tills", "åt", "upp", "på", "oss", "använda", "används", "användbar", "använder", "användning", "vanligtvis", "uucp", "värde", "olika", "mycket", "via", "viz", "vs", "vill", "vill", "var", "var inte", "sätt", "vi", "vi skulle", "vi kommer", "vi är", "vi har", "välkommen", "väl", "gick", "var", "var inte", "vad", "vad är", "oavsett", "när", "varifrån", "närhelst", "där", "var är", "varefter", "medan", "varigenom", "vari", "varpå", "varhelst", "huruvida", "som", "medan", "dit", "som", "vem är", "vem", "hela", "vem", "vars", "varför", "kommer", "villig", "önskar", "med", "inom", "utan", "kommer inte", "undrar", "skulle", "skulle inte", "ja", "ännu", "ni", "du skulle", "kommer du", "du är", "du har", "din", "själv", "er", "noll", "tjänsteman", "skarpt", "kritiserade", ])
ideal = 20.0


def SummarizeUrl(url):
    summaries = []
    try:
        article = grab_link(url)
    except IOError:
        print 'IOError'
        return None

    if not (article and article.cleaned_text and article.title):
        return None

    summaries = Summarize(unicode(article.title),
                          unicode(article.cleaned_text))
    return summaries


def Summarize(title, text, sentence_count=5):
    summaries = []
    sentences = split_sentences(text)
    keys = keywords(text)
    titleWords = split_words(title)

    if len(sentences) <= sentence_count:
        return sentences

    #score setences, and use the top 5 sentences
    ranks = score(sentences, titleWords, keys).most_common(sentence_count)
    for rank in ranks:
        summaries.append(rank[0])

    return summaries


def grab_link(inurl):
    #extract article information using Python Goose
    from goose import Goose
    try:
        article = Goose().extract(url=inurl)
        return article
    except ValueError:
        print 'Goose failed to extract article from url'
        return None
    return None


def score(sentences, titleWords, keywords):
    #score sentences based on different features

    senSize = len(sentences)
    ranks = Counter()
    for i, s in enumerate(sentences):
        sentence = split_words(s)
        titleFeature = title_score(titleWords, sentence)
        sentenceLength = length_score(sentence)
        sentencePosition = sentence_position(i+1, senSize)
        sbsFeature = sbs(sentence, keywords)
        dbsFeature = dbs(sentence, keywords)
        frequency = (sbsFeature + dbsFeature) / 2.0 * 10.0

        #weighted average of scores from four categories
        totalScore = (titleFeature*1.5 + frequency*2.0 +
                      sentenceLength*1.0 + sentencePosition*1.0) / 4.0
        ranks[s] = totalScore
    return ranks


def sbs(words, keywords):
    score = 0.0
    if len(words) == 0:
        return 0
    for word in words:
        if word in keywords:
            score += keywords[word]
    return (1.0 / fabs(len(words)) * score)/10.0


def dbs(words, keywords):
    if (len(words) == 0):
        return 0

    summ = 0
    first = []
    second = []

    for i, word in enumerate(words):
        if word in keywords:
            score = keywords[word]
            if first == []:
                first = [i, score]
            else:
                second = first
                first = [i, score]
                dif = first[0] - second[0]
                summ += (first[1]*second[1]) / (dif ** 2)

    # number of intersections
    k = len(set(keywords.keys()).intersection(set(words))) + 1
    return (1/(k*(k+1.0))*summ)


def split_words(text):
    #split a string into array of words
    try:
        text = regex_sub(r'[^\w ]', '', text, flags=REGEX_UNICODE)  # strip special chars
        return [x.strip('.').lower() for x in text.split()]
    except TypeError:
        print "Error while splitting characters"
        return None


def keywords(text):
    """get the top 10 keywords and their frequency scores
    ignores blacklisted words in stopWords,
    counts the number of occurrences of each word
    """
    text = split_words(text)
    numWords = len(text)  # of words before removing blacklist words
    freq = Counter(x for x in text if x not in stopWords)

    minSize = min(10, len(freq))  # get first 10
    keywords = {x: y for x, y in freq.most_common(minSize)}  # recreate a dict

    for k in keywords:
        articleScore = keywords[k]*1.0 / numWords
        keywords[k] = articleScore * 1.5 + 1

    return keywords


def split_sentences(text):
    '''
    The regular expression matches all sentence ending punctuation and splits the string at those points.
    At this point in the code, the list looks like this ["Hello, world", "!" ... ]. The punctuation and all quotation marks
    are separated from the actual text. The first s_iter line turns each group of two items in the list into a tuple,
    excluding the last item in the list (the last item in the list does not need to have this performed on it). Then,
    the second s_iter line combines each tuple in the list into a single item and removes any whitespace at the beginning
    of the line. Now, the s_iter list is formatted correctly but it is missing the last item of the sentences list. The
    second to last line adds this item to the s_iter list and the last line returns the full list.
    '''

    sentences = regex_split(u'(?<![A-ZА-ЯЁ])([.!?]"?)(?=\s+\"?[A-ZА-ЯЁ])', text, flags=REGEX_UNICODE)
    s_iter = zip(*[iter(sentences[:-1])] * 2)
    s_iter = [''.join(y).lstrip() for y in s_iter]
    s_iter.append(sentences[-1])
    return s_iter



def length_score(sentence):
    return 1 - fabs(ideal - len(sentence)) / ideal


def title_score(title, sentence):
    title = [x for x in title if x not in stopWords]
    count = 0.0
    for word in sentence:
        if (word not in stopWords and word in title):
            count += 1.0
            
    if len(title) == 0:
        return 0.0
        
    return count/len(title)


def sentence_position(i, size):
    """different sentence positions indicate different
    probability of being an important sentence"""

    normalized = i*1.0 / size
    if 0 < normalized <= 0.1:
        return 0.17
    elif 0.1 < normalized <= 0.2:
        return 0.23
    elif 0.2 < normalized <= 0.3:
        return 0.14
    elif 0.3 < normalized <= 0.4:
        return 0.08
    elif 0.4 < normalized <= 0.5:
        return 0.05
    elif 0.5 < normalized <= 0.6:
        return 0.04
    elif 0.6 < normalized <= 0.7:
        return 0.06
    elif 0.7 < normalized <= 0.8:
        return 0.04
    elif 0.8 < normalized <= 0.9:
        return 0.04
    elif 0.9 < normalized <= 1.0:
        return 0.15
    else:
        return 0
