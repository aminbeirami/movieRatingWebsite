from lib import postgresCon as pc
import functools
from lib import keyGen as kg
from random import randint
from lib.config import *
from time import sleep
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
	sql = "SELECT pg_size_pretty(pg_total_relation_size('timeline'))"
	result = db.query(sql,None,'one')
	int_size = [int(s) for s in result[0].split() if s.isdigit()]
	alpha_size = [a for a in result[0].split() if a.isalpha()]
	if alpha_size[0] =='kB':
		int_size[0] *=1000
	elif(alpha_size[0] =='MB'):
		int_size[0] *=1000000
	elif(alpha_size[0] == 'GB'):
		int_size[0] *=1000000000
	return int_size[0]
