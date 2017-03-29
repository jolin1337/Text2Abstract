import re, ast


def filterArticlesFromCSV(inputFile, outputFile, filter):
	csv = open(inputFile, 'r')
	out = open(outputFile, 'w')
	headline = 0
	headlineArray = []

	for line in csv:
		columns = line[1:-2].split('"§§"')
		if headline == 0:
			# out.write('"' + '"§§"'.join(columns) + '"\n')
			headlineArray = columns # {c: i for i, c in enumerate(columns)}
		filtered = {headlineArray[i]: c for i, c in enumerate(columns)}
		try:
			filtered = filter({c: i for i, c in enumerate(headlineArray)}, columns)
			if headline != 2:
				headline = 1
		except Exception as e:
			print headlineArray, {c: i for i, c in enumerate(headlineArray)}
			raise
			continue
		if filtered == False:
			continue
		if headline == 1:
			print '"' + '"§§"'.join(filtered.keys()) + '"\n'
			if filtered == True:
				out.write('"' + '"§§"'.join(columns) + '"\n')
			else:
				out.write('"' + '"§§"'.join(filtered.keys()) + '"\n')
			headline = 2
			continue

		out.write(('"' + u'"§§"'.join(filtered.values()) + '"\n').encode('utf-8'))
	out.close()
	csv.close()


shouldContainTextRegexp = re.compile('([a-zA-Z]+[ .\t\n]){10,}')
def rawJsonFilter(headline, columns):
	if 'uuid' in columns or 'data' in columns:
		return False
	rawJson = ast.literal_eval(unicode(columns[headline['data']]))
	if rawJson['body'] and rawJson['body'].find('uuid') < 0 and len(rawJson['categories']) > 0 and None != shouldContainTextRegexp.search(rawJson['body']):
		return {
			'uuid': columns[headline['uuid']],
			'body': rawJson['body'],
			'categories': str(rawJson['categories'])
		}

	else:
		return False

def printAnomalies(inputFile):
	csv = open(inputFile, 'r')
	headline = False
	smallestDocuments = [None] * 1
	largestDocuments = [None] * 1

	for line in csv:
		columns = line[1:-2].split('"§§"')
		if headline == False:
			headline = {c: i for i, c in enumerate(columns)}
			continue

		currentDocument = columns[headline['body']].split(" ")
		for i, smallestDocument in enumerate(smallestDocuments):
			if not smallestDocument or len(smallestDocument[headline['body']]) > len(currentDocument):
				smallestDocuments[i] = columns
				smallestDocuments[i][headline['body']] = currentDocument
				break
		
		for i, largestDocument in enumerate(largestDocuments):
			if not largestDocument or len(largestDocument[headline['body']]) < len(currentDocument):
				largestDocuments[i] = columns
				largestDocuments[i][headline['body']] = currentDocument

	if headline:
		for largestDocument in largestDocuments:
			print "---------- Largest document ", smallestDocument[headline['uuid']], "  ----------"
			print largestDocument[headline['categories']]
			print ' '.join(largestDocument[headline['body']])
		for smallestDocument in smallestDocuments:
			print "---------- Smallest document ", smallestDocument[headline['uuid']], " ----------"
			print smallestDocument[headline['categories']]
			print ' '.join(smallestDocument[headline['body']])

if __name__ == '__main__':
	import dotenv
	dotenv.load()

	filterArticlesFromCSV(dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_mars_28_1140', dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_mars_28_1140-filter-uuid', rawJsonFilter)
	printAnomalies(dotenv.get('ARTICLE_PATH', '.') + '/tmp-articles-dump_mars_28_1140-filter-uuid')
