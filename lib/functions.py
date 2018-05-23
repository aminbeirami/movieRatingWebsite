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

def records_count(table_name): # returns number of movies in the database
	sql = "SELECT COUNT(*) FROM {0}".format(table_name)
	result = db.query(sql,None,"one")
	return result[0]

def table_attribs(table_name):
	sql = "SELECT column_name FROM information_schema.columns WHERE table_name = %s"
	parameters = (table_name,)
	result = db.query(sql,parameters,"all")
	result_list = [index[0] for index in result]
	return result_list

def make_dict(attribs,data):
	dictonary = dict(zip([x for x in attribs],[y for y in data]))
	return dictonary

def random_user(): #chooses a random user from database
	user_id = randint(0,records_count('users'))
	sql = "SELECT * FROM users WHERE user_id = %s"
	parameters = (user_id,)
	usr_attribs = table_attribs('users')
	usr_data = db.query(sql,parameters,'one')
	usr_dictionary = make_dict(usr_attribs,usr_data)
	return usr_dictionary 

def random_movie(): #chooses a random movie name from database
	movie_id = randint(0,records_count('movies'))
	sql = "SELECT * FROM movies WHERE mov_id = (%s)"
	parameters = (movie_id,)
	movie_attribs = table_attribs('movies')
	movie_data = db.query(sql,parameters,'one')
	movie_dictionary = make_dict(movie_attribs,movie_data)
	return movie_dictionary

def movie_id_list():
	sql = "SELECT id FROM rating"
	ids = db.query(sql,None,'all')
	return [x[0] for x in ids]

def insert_parameters(user,movie,rating):
	parameters = [movie['mov_id'],movie['mv_name'],movie['mv_year'],movie['release_date'],movie['movie_url'],rating,user['user_id'],user['username']]
	return parameters

def create_signature(raw_parameters,username):
	sql = "SELECT private_key FROM users WHERE username = (%s)"
	parameters = (username,)
	key = db.query(sql,parameters,'one')
	data = ''.join([str(x for x in raw_parameters)])
	keyGen = kg.RSAEncryption()
	signature = keyGen.generate_signature(data,key)
	return signature



