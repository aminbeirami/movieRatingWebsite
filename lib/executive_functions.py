from lib import functions as fcn
from lib import postgresCon as pc
from lib.config import *
from random import randint, randrange
from datetime import datetime
from sklearn.cluster import KMeans
import datetime as dt
import random
import time
import threading

db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)

# **************************************************** SNAPSHOT CREATION FUNCTIONS ***************************************************************
def get_snap_id():
	sql = "SELECT NEXTVAL('{0}')".format('snap_id')
	result = db.query(sql,None,'one')
	return result[0] 

def create_first_value_clause(attributes):
	clause = ",\n".join(
		"first_value({c}) over w as {c}".format(c=x) for x in attributes)
	return clause

def create_snapshots(rel_name,timestamp):
	snap_id = get_snap_id()
	snapshot_name = "{0}__{1}".format(rel_name,str(snap_id))
	attributes = [x for x in fcn.table_attribs(rel_name) if not x == 'id']
	f_value_clause = create_first_value_clause(attributes)
	sql = '''
		CREATE TABLE IF NOT EXISTS {snap_name} AS 
		SELECT * FROM (
			SELECT
				id,
				{latest_attributes},
				first_value(__flag__) over w AS  flag
				FROM {timeline_table}
				WHERE __t__<= %s
				window w AS (partition by id ORDER BY __t__ desc)) T
	'''.format(snap_name = snapshot_name, timeline_table = 'timeline',latest_attributes = f_value_clause)
	parameters = [timestamp,]
	db.command(sql,parameters)
	db.commit()
# ******************************************* RANDOM INSERTION,DELETION AND UPDATE fUNCTIONS *****************************************************

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
	return {'action':'insert','user':user['username'],'movie':movie['mv_name'],'rating':random_rating,'position':[user['lat'],user['long']],'time':str(datetime.now())}


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
		user_location['long']],
		'time':str(datetime.now())}
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
	user_location['long']],
	'time':datetime.now()}

# ********************************************************** SIMULATION FUNCTIONS ************************************************************

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

def random_query_generator():
	fmt = '%Y-%m-%d %H:%M:%S'
	duration = fcn.timeline_duration()
	start = duration['min']
	end = duration['max']
	second_difference = fcn.calc_sec_difference(start,end)
	query_list = fcn.create_query_clusters(second_difference,20,100)
	random_dates = []
	for i in range(len(query_list)):
		random_dates.append(start + dt.timedelta(seconds = query_list[i]))
	return random_dates
	# print randrange(int(second_difference))
	# curr = current + datetime.timedelta(seconds = randrange(int(second_difference)))

#********************************************************* SNAPSHOT MATERIALIZATION FUNCTIONS ********************************************
def make_query_list_2D(queries):
	new_query_list = []
	for i in range(len(queries)):
		new_query_list.append((queries[i],0))
	return new_query_list

def query_clustering(queries,no_clusters):
	kmeans = KMeans(n_clusters= no_clusters, init = 'k-means++',max_iter = 300, n_init = 10, random_state = 0)
	y_kmeans = kmeans.fit_predict(queries)
	return y_kmeans, kmeans.cluster_centers_

def recommend_no_clusters(query_data,max_snapshot): #elbow method in clustering
	cost = []
	for i in range(1,max_snapshot+1):
		kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
		y_kmeans = kmeans.fit_predict(query_data)
		cost.append(kmeans.inertia_)
	return cost

def create_clusters(query_list):
	duration = fcn.timeline_duration()
	query_date_to_number = []
	for i in range(len(query_list)):
		query_date_to_number.append(fcn.calc_sec_difference(duration['min'],query_list[i]))
	query_list_2D = make_query_list_2D(query_date_to_number)
	recommended = recommend_no_clusters(query_list_2D,10)
	clustered_list,centroids = query_clustering(query_list_2D,6)
	print clustered_list
	print centroids
	