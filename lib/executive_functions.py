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
	return {'action':'insert','user':user['username'],'movie':movie['mv_name'],'rating':random_rating,'position':[user['lat'],user['long']]}


def random_delete(): #deletes random number of records
	random_record = fcn.fetch_specific_attribs_record(['id','user_id','username','mv_name','star'],'rating','ORDER BY RANDOM() LIMIT 1')
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record['user_id']))
	try:
		sql = "DELETE FROM rating WHERE id =(%s)"
		parameters = (random_record['id'],)
		db.command(sql,parameters)
		db.commit()
		return {'action':'delete',\
		'user':random_record['username'],\
		'movie':random_record['mv_name'],\
		'rating':random_record['star'],\
		'position':[user_location['lat'],\
		user_location['long']]}
	except Exception as e:
		print e
		return 'error'
  
def random_update():
	random_rating = randint(1,5)
	random_record = fcn.fetch_specific_attribs_record(['id','user_id','username','mv_name','star'],'rating','ORDER BY RANDOM() LIMIT 1')
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record['user_id']))
	sql = "UPDATE rating SET star = (%s) WHERE id =(%s)"
	parameters = (random_rating,random_record['id'])
	db. command(sql,parameters)
	db.commit()
	return {'action':'update',\
	'user':random_record['username'],\
	'movie':random_record['mv_name'],\
	'rating':random_record['star'],\
	'position':[user_location['lat'],\
	user_location['long']]}

def random_rating(permission):
	random_action = randint(1,3)
	switcher = {
		1: random_insert,
		2: random_update,
		3: random_delete,
	}
	if permission == True:
		action_result = switcher[random_action]()
	else:
		if random_action == 3:
			action_result = switcher[1]()
		else:
			action_result = switcher[random_action]()
	return action_result