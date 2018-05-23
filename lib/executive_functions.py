from lib import functions as fcn
from lib import postgresCon as pc
from lib.config import *
from random import randint
import random

db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)

def random_insert(): #insrts random records to the main database
	random_rating = randint(1,5)
	user = fcn.random_user()
	movie = fcn.random_movie()
	rating_attribs = [x for x in fcn.table_attribs('rating') if not x == 'id']
	sql = "INSERT INTO rating VALUES(NEXTVAL('rating_id_seq'),%s)"%",".join("%s" for i in range(len(rating_attribs)))
	parameters = fcn.insert_parameters(user,movie,random_rating)
	signature = fcn.create_signature(parameters,user['username'])
	parameters.append(signature)
	db.insert(sql,parameters)
	db.commit()
	# print 'the movie '+ movie[0] + ' by user '+str(usr[0])+ ' located at '+ str(usr[1])+ '-'+ str(usr[2])+ ' received '+str(random_rating)+ ' stars.'
	print 'inserted'

def random_delete(): #deletes random number of records
  random_records = randint(1,fcn.records_count('rating')//2)
  # print random_records
  sql = "DELETE FROM rating WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT %s)"
  parameters = (random_records,)
  db.command(sql,parameters)
  db.commit()
  print str(random_records) + " number of records deleted"

def random_update(): #randomly chooses a record and updates it
  random_records = randint(1,fcn.records_count('rating'))
  random_rating = randint(1,5)
  sql = "UPDATE rating SET star = (%s) WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT %s)"
  parameters = (random_rating,random_records)
  db. command(sql,parameters)
  db.commit()
  # print str(random_records) + " number of records updated."

def random_rating(permission):
	for i in range(0,100):
		if permission == True:
			random_insert()
			random_update()
			if i%50 == 0:
				random_delete()
		else:
			random_insert()
			random_update()