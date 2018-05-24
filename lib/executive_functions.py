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
	print {'action':'insert','user':user['username'],'movie':movie['mv_name'],'rating':random_rating,'position':[user['lat'],user['long']]}
	# print 'inserted'

def random_delete(): #deletes random number of records
  try:
	sql = "DELETE FROM rating WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT 1)"
	db.command(sql,None)
	db.commit()
	print 'deleted'
  except Exception as e:
  	print e
  
  
def random_update():
	random_rating = randint(1,5)
	sql = "SELECT * FROM rating ORDER BY RANDOM() LIMIT 1"
	result = db.query(sql,None,'one')
	sql = "UPDATE rating SET star = (%s) WHERE id =(%s)"
	parameters = (random_rating,result[0])
	db. command(sql,parameters)
	db.commit()

	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','user_id = {0}'.format(result[6]))
	print {'action':'update','user':result[8],'movie':result[2],'rating':result[6],'position':[user_location['lat'],user_location['long']]}

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