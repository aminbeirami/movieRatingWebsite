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


def random_user(): #chooses a random user from database
	user_id = randint(0,1000)
	sql = "SELECT * FROM users WHERE user_id = (%s)"
	parameters = (user_id,)
	usr_data = db.query(sql,parameters,'one')
	return usr_data

def random_movie(): #chooses a random movie name from database
	movie_id = randint(0,1682)
	sql = "SELECT mv_name FROM movies WHERE mov_id = (%s)"
	parameters = (movie_id,)
	movie_name = db.query(sql,parameters,'one')
	return movie_name

def records_no(): # returns random number of records in the main database
	sql = "SELECT COUNT(*) FROM rating"
	size = db.query(sql,None,'one')
	return size[0]

def random_insert (): #insrts random records to the main database
	random_rating = randint(1,5)
	usr = random_user()
	movie = random_movie()
	sql = "INSERT INTO rating(usr_id,mv_name,rating,lat,long) VALUES(%s,%s,%s,%s,%s)"
	parameters = (usr[0],movie[0],random_rating,usr[1],usr[2])
	db.insert(sql,parameters)
	print 'the movie '+ movie[0] + ' by user '+str(usr[0])+ ' located at '+ str(usr[1])+ '-'+ str(usr[2])+ ' received '+str(random_rating)+ ' stars.'

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

