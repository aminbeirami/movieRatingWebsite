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

def random_insert(): #insrts random records to the main database
	random_rating = randint(1,5)
	user = random_user()
	movie = random_movie()
	rating_attribs = [x for x in table_attribs('rating') if not x == 'id']
	sql = "INSERT INTO rating VALUES(NEXTVAL('rating_id_seq'),%s)"%",".join("%s" for i in range(len(rating_attribs)))
	parameters = insert_parameters(user,movie,random_rating)
	signature = create_signature(parameters,user['username'])
	parameters.append(signature)
	db.insert(sql,parameters)
	# print 'the movie '+ movie[0] + ' by user '+str(usr[0])+ ' located at '+ str(usr[1])+ '-'+ str(usr[2])+ ' received '+str(random_rating)+ ' stars.'

def random_delete(): #deletes random number of records
  random_records = randint(1,records_no()/2)
  sql = "DELETE FROM rating WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT %s)"
  parameters = (random_records,)
  db.command(sql,parameters)
  db.commit()
  print str(random_records) + " number of records deleted"

def random_update(): #randomly chooses a record and updates it
  random_records = randint(1,records_no())
  random_rating = randint(1,5)
  sql = "UPDATE rating SET rating = (%s) WHERE id IN (SELECT id FROM rating ORDER BY RANDOM() LIMIT %s)"
  parameters = (random_rating,random_records)
  db. command(sql,parameters)
  db.commit()
  print str(random_records) + " number of records updated."

def random_rating():
	for i in range(0,100):
		random_insert()
		random_update()
		# random_delete()

