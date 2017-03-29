#!/bin/bash
# -*- coding: utf-8 -*-


# sudo -i -u postgres # switch user to postgres to access database
# psql # postgres commandprompt

#      ('public', 'articles')
#      ('public', 'collections')
#      ('public', 'schema_migrations')
#      ('public', 'slugs')

import re
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

import psycopg2
import psycopg2.extras

def getCategories(cur):

	cur.execute("""
		SELECT  DISTINCT (data->'categories'->0->0->'name')
		FROM public.articles66
		WHERE json_array_length(data->'categories'->0) = 1 
		  AND data #>> '{state}' = 'USABLE'
		  AND data #>> '{contenttype}' = 'Article';
	""")

	rows = cur.fetchall()
	for row in rows:
		for col in row:
			if isinstance(col, basestring):
				print row

def getArticles(cur, limit=100000, offset=0):
	cur.execute("""
		SELECT  uuid, data
		--		data->'headline' as headline, 
		--		data->'body' as body, 
		--		data->'categories'->0->0->'name' as first_category
		FROM public.articles
		--WHERE json_array_length(data->'categories'->0) = 1 
		--  AND data #>> '{state}' = 'USABLE'
		--  AND data #>> '{contenttype}' = 'Article'
		--ORDER BY data->'publish_at'
		LIMIT %s
		OFFSET %s;
	""" % (limit, offset))
	# cur.execute("""
	# 	SELECT  *
	# 	FROM public.articles
	# 	LIMIT %s;
	# """ % limit)

	column_names = [desc[0] for desc in cur.description]
	rows = cur.fetchall()
	print '"' + '"§§"'.join(column_names) + '"'
	for row in rows:
		csvInstance = ""
		for i, col in enumerate(row):
			if i > 0:
				csvInstance += '"§§"'
			if not isinstance(col, basestring):
				col = str(col)
			csvInstance += striphtml(col.replace("\n", ' ').replace("§", '')).encode('UTF-8')
		while csvInstance.find("\n") > -1:
			csvInstance = csvInstance.replace("\n", ' ')
		#csvInstance = csvInstance
		#print csvInstance.find("\n")
		print '"' + csvInstance + '"'

if __name__ == '__main__':
	conn = None
	try:
		conn = psycopg2.connect("dbname='" + dbname + "' user='" + user + "' host='" + host + "' password='" + password + "'")

	except:
		print "I am unable to connect to the database"
	if conn: 
		cur = conn.cursor() # add this arg if u want column names: cursor_factory=psycopg2.extras.DictCursor)
		
		
		getArticles(cur, 100)