from lib import postgresCon as pc
import functools
from lib import keyGen as kg
from random import randint
from lib.config import *
from time import sleep
from datetime import datetime
import numpy as np
# from lib import thread_timer as tm

from threading import Event, Thread

def call_repeatedly(interval, func, *args):
    stopped = Event()
    def loop():
        while not stopped.wait(interval): # the first call is in `interval` secs
            func(*args)
    Thread(target=loop).start()    
    return stopped.set

db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)


def table_attribs(table_name):
	sql = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
	parameters = (table_name,)
	result = db.query(sql,parameters,"all")
	result_list = [index[0] for index in result]
	return result_list

def make_dict(attribs,data):
	dictonary = dict(zip([x for x in attribs],[y for y in data]))
	return dictonary

def fetch_everything_record(table_name,condition):
	sql = "SELECT * FROM {0} {1}".format(table_name,condition)
	rec_data = db.query(sql,None,'one')
	rec_attribs = table_attribs(table_name)
	rec_dictionary = make_dict(rec_attribs,rec_data)
	return rec_dictionary

def fetch_specific_attribs_record(attribs,table_name,condition):
	result = {}
	rec_dictionary = fetch_everything_record(table_name,condition)
	for i in attribs:
		result[i]=rec_dictionary[i]
	return result

def records_count(table_name): # returns number of movies in the database
	sql = "SELECT COUNT(*) FROM {0}".format(table_name)
	result = db.query(sql,None,"one")
	return result[0]

def random_user(): #chooses a random user from database
	user_id = randint(0,records_count('users'))
	user_data = fetch_everything_record('users','where user_id = {0}'.format(user_id))
	return user_data 

def random_movie(): #chooses a random movie name from database
	movie_id = randint(0,records_count('movies'))
	movie_data = fetch_everything_record('movies','where mov_id = {0}'.format(movie_id))
	return movie_data

def movie_id_list():
	sql = "SELECT id FROM rating"
	ids = db.query(sql,None,'all')
	return [x[0] for x in ids]

def insert_parameters(user,movie,rating):
	parameters = [movie['mov_id'],movie['mv_name'],movie['mv_year'],movie['release_date'],movie['movie_url'],rating,user['user_id'],user['username']]
	return parameters

def create_signature(raw_parameters,username):
	key = fetch_specific_attribs_record(['private_key',],'users',"where username = '{0}'".format(username))
	data = ''.join([str(x for x in raw_parameters)])
	keyGen = kg.RSAEncryption()
	signature = keyGen.generate_signature(data,key['private_key'])
	return signature

def table_size():
	sql = "select pg_relation_size('rating');"
	result = db.query(sql,None,'one')
	return {'size': int(result[0]),'time_checked':datetime.now()}

def timeline_duration():
	sql = "SELECT MAX(__t__) FROM timeline"
	max_date = db.query(sql,None,'one')[0]
	sql = "SELECT MIN(__t__) FROM timeline"
	min_date = db.query(sql,None,'one')[0]
	return {'min': min_date, 'max':max_date}

def calc_sec_difference(base_date, query_date):
	second_difference = int((query_date-base_date).total_seconds())
	return second_difference

def create_query_clusters(bound,no_clusters,scale):
	sections = int(bound/no_clusters)
	section_bounds = []
	lower_bound = 0
	for i in range(1,no_clusters+1):
		bound = lower_bound+sections
		section_bounds.append(bound)
		lower_bound = bound
	queries = []
	for i in range(no_clusters):
		if i ==0:
			queries.append(np.random.normal(randint(0,section_bounds[i+1]),4,scale))
		else:
			queries.append(np.random.normal(randint(section_bounds[i-1],section_bounds[i]),4,scale))
	query_list=[]
	for i in range(len(queries)):
		for j in range(len(queries[i])):
			query_list.append(queries[i][j])
	return query_list
