from lib import functions as fcn
from lib import postgresCon as pc
from lib.config import *
from random import randint
import random
import time
import threading

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
	print 'inserted'

def random_delete(): #deletes random number of records
  try:
	sql = "DELETE FROM rating WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT 1)"
	db.command(sql,None)
	db.commit()
	print 'deleted'
  except Exception as e:
  	print e
  
  
def random_update(): #randomly chooses a record and updates it
  random_rating = randint(1,5)
  sql = "UPDATE rating SET star = (%s) WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT 1)"
  parameters = (random_rating,)
  db. command(sql,parameters)
  db.commit()
  print 'updated'

def random_rating(permission):
	random_action = randint(1,3)
	switcher = {
		1: random_insert,
		2: random_update,
		3: random_delete,
	}
	if permission == True:
		switcher[random_action]()
	else:
		if random_action == 3:
			switcher[1]()
		else:
			switcher[random_action]()