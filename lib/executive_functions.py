#BY AMIN BEIRAMI -- beirami.m.a@gmail.com
#EXECUTIVE FUNCTIONS
from lib import functions as fcn
from lib import postgresCon as pc
from lib.config import *
from random import randint, randrange
from datetime import datetime
from sklearn.cluster import KMeans
import datetime as dt
import numpy as np
import random
import time
import threading

db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)
clsuter_info = {'clusters':[],'snapshots':[]}

# **************************************************** SNAPSHOT CREATION FUNCTIONS ***************************************************************
def get_snap_id():
	sql = "SELECT NEXTVAL('{0}')".format('snap_id')
	result = db.query(sql,None,'one')
	return result[0] 

def create_first_value_clause(attributes):
	# clause = ",\n".join("first_value({c}) over w as {c}".format(c=x) for x in attributes)
	clause = ",\n".join("last_value({c}) over (partition by rec_id order by __t__ RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as {c}".format(c=x) for x in attributes)
	return clause

def create_snapshots(rel_name,timestamp):
	snap_id = get_snap_id()
	snapshot_name = "{0}__{1}".format(rel_name,str(snap_id))
	attributes = [x for x in fcn.table_attribs(rel_name) if not x == 'id']
	f_value_clause = create_first_value_clause(attributes)

	sql = '''
	CREATE TABLE IF NOT EXISTS {snap_name} AS
	SELECT DISTINCT
	rec_id,
	{latest_attributes},
	max(__t__) OVER (PARTITION BY rec_id) AS __t__
	FROM {timeline_table}
	WHERE __flag__=0 AND __t__ <=%s
	'''.format(snap_name = snapshot_name, latest_attributes = f_value_clause,timeline_table = 'timeline')
	# sql = '''
	#  	CREATE TABLE IF NOT EXISTS {snap_name} AS 
	#  	SELECT DISTINCT * FROM (
	#  		SELECT
	#  			rec_id,
	#  			{latest_attributes},
	#  			max(__t__) OVER w AS __t__,
	#  			first_value(__flag__) over w AS  flag
	#  			FROM {timeline_table}
	#  			WHERE __t__<= %s AND __flag__ =0
	#  			window w AS (partition by rec_id ORDER BY __t__ DESC)) T
	#  '''.format(snap_name = snapshot_name, timeline_table = 'timeline',latest_attributes = f_value_clause)

	parameters = [timestamp,]
	print sql
	db.command(sql,parameters)
	db.commit()
# ******************************************* RANDOM INSERTION,DELETION AND UPDATE fUNCTIONS *****************************************************

def random_insert(): #insrts random records to the main database
	random_rating = randint(1,5)
	user = fcn.random_user()
	movie = fcn.random_movie()
	rating_attribs = [x for x in fcn.table_attribs('rating')]
	record_id = db.query("SELECT NEXTVAL('rating_id_seq')",None,"one")[0]
	sql = "INSERT INTO rating VALUES(%s)"%",".join("%s" for i in range(len(rating_attribs)))
	parameters = fcn.insert_parameters(user,movie,random_rating)
	parameters.insert(0,record_id)
	signature = fcn.create_signature(parameters,user['username'])
	parameters.append(signature)
	db.insert(sql,parameters)
	db.commit()
	print 'insert'
	return {'action':'insert','user':user['username'],'movie':movie['mv_name'],'rating':random_rating,'position':[user['lat'],user['long']],'time':str(datetime.now())}


def random_delete(): #deletes random number of records
	attribs = [x for x in fcn.table_attribs('rating') if not x == 'signature']
	random_record_list = list(fcn.fetch_specific_record_list(attribs,'rating','ORDER BY RANDOM() LIMIT 1'))
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record_list[7]))
	try:
		sql = "DELETE FROM rating WHERE id =(%s)"
		parameters = (random_record_list[0],)
		db.command(sql,parameters)
		db.commit()
		for i in range(1,len(random_record_list)-1):
			random_record_list[i] = None
		signature = fcn.create_signature(random_record_list,random_record_list[8])
		record_id = fcn.fetch_specific_record_list(['last_value',],'id','')[0]
		sql = "UPDATE timeline SET signature = (%s) WHERE id = (%s)"
		parameters = [signature,record_id]
		db.command(sql,parameters)
		db.commit()
		print 'delete'
		return {'action':'delete','user':random_record_list[8],'movie':random_record_list[2],'rating':random_record_list[6],'position':[user_location['lat'],user_location['long']],'time':str(datetime.now())}
	except Exception as e:
		print e
		return 'error'
  
def random_update():
	random_rate = randint(1,5)
	attribs = [x for x in fcn.table_attribs('rating') if not x == 'signature']
	random_record_list = list(fcn.fetch_specific_record_list(attribs,'rating','ORDER BY RANDOM() LIMIT 1'))
	random_record_dict = fcn.fetch_specific_attribs_record(attribs,'rating', 'WHERE id ={0}'.format(random_record_list[0]))
	random_record_list[6] = random_rate
	signature = fcn.create_signature(random_record_list,random_record_dict['username'])
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record_dict['user_id']))
	sql = "UPDATE rating SET star = (%s), signature = (%s) WHERE id =(%s)"
	parameters = (random_rate,signature,random_record_dict['id'])
	db.command(sql,parameters)
	db.commit()
	print 'update'
	return {'action':'update','user':random_record_dict['username'],'movie':random_record_dict['mv_name'],'rating':random_record_dict['star'],'position':[user_location['lat'],	user_location['long']],'time':datetime.now()}

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
	duration = fcn.table_duration('timeline')
	start = duration['min']
	end = duration['max']
	second_difference = fcn.calc_sec_difference(start,end)
	query_list = fcn.create_query_clusters(second_difference,20,100)
	random_dates = []
	for i in range(len(query_list)):
		random_dates.append(start + dt.timedelta(seconds = query_list[i]))
		# random_dates.append(fcn.calc_time_from_seconds(start,query_list[i]))
	return random_dates
	# print randrange(int(second_difference))
	# curr = current + datetime.timedelta(seconds = randrange(int(second_difference)))

#********************************************************* CLUSTERING FUNCTIONS ***********************************************************
def make_query_list_2D(queries):
	new_query_list = []
	queries = sorted(queries)
	for i in range(len(queries)):
		new_query_list.append((queries[i],0))
	return new_query_list

def optimal_snap_positions(query_clusters,base_date):
	snapshot_positions = []
	for i in range(len(query_clusters)):
		snapshot_positions.append(fcn.calc_time_from_seconds(np.median(query_clusters[i]),base_date))
	return sorted(snapshot_positions)

def fetch_clustered_info(queries,clusters,no_clusters,base_date):
	cluster_of_queries_sec = []
	cluster_of_queries_date = []
	for i in range(no_clusters):
		cluster_of_queries_sec.append([])
		cluster_of_queries_date.append([])
	for j in range(no_clusters):
		for s in range(len(queries)):
			if clusters[s] == j:
				cluster_of_queries_sec[j].append(queries[s][0])
				cluster_of_queries_date[j].append(fcn.calc_time_from_seconds(queries[s][0],base_date))
	snapshot_positions = optimal_snap_positions(cluster_of_queries_sec,base_date)
	return	cluster_of_queries_date,snapshot_positions

def query_clustering(queries,no_clusters):
	kmeans = KMeans(n_clusters= no_clusters, init = 'k-means++',max_iter = 300, n_init = 10, random_state = 0)
	y_kmeans = kmeans.fit_predict(queries)
	print y_kmeans
	return y_kmeans, kmeans.cluster_centers_

def recommend_no_clusters(query_data,max_snapshot): #elbow method in clustering
	cost = []
	for i in range(1,max_snapshot+1):
		kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
		y_kmeans = kmeans.fit_predict(query_data)
		cost.append(kmeans.inertia_)
	return cost

def create_clusters(query_list):
	cluster_dates = []
	snapshot_positions_date = []
	duration = fcn.table_duration('timeline')
	query_in_seconds = []
	for i in range(len(query_list)):
		query_in_seconds.append(fcn.calc_sec_difference(duration['min'],query_list[i]))
	query_list_2D = make_query_list_2D(query_in_seconds)
	recommended = recommend_no_clusters(query_list_2D,10) #elbow method to find the optimal snapshot numbers
	clustered_list,centroids = query_clustering(query_list_2D,6)
	query_clusters,snapshot_positions = fetch_clustered_info(query_list_2D,clustered_list,6,duration['min'])
	clsuter_info['clusters'] = query_clusters
	clsuter_info['snapshots'] = snapshot_positions
	return clsuter_info
	# snapshot_positions_seconds = optimal_snap_positions(query_clusters,duration['min'])
	# for i in range(len(clustered_list)):
	# 	print clustered_list[i]

#*********************************************** SNAPSHOT MATERIALIZATION FUNCTIONS *************************************************

def choose_names(type,rel_name):
	if type == 'query':
		snapshot_name = 'query__{0}'.format(query_id)
		temp_snapshot_name = 'temp__{0}'.format(query_id)
	elif type == 'snapshot':
		snap_id = get_snap_id()
		snapshot_name = "{0}__{1}".format(rel_name,str(snap_id))
		temp_snapshot_name = "temp_{0}__{1}".format(rel_name,str(snap_id))
	else:
		print 'invalid request'
	return snapshot_name,temp_snapshot_name


def union_snapshot_and_query(temp_snapshot_name,timeline_table,f_value_clause,query_timestamp,materialized):
	start_timestamp = fcn.table_duration(materialized)['max']
	sql = '''
	CREATE TABLE IF NOT EXISTS {temp} AS
	SELECT DISTINCT * FROM (
		SELECT rec_id,
		{latest_attributes},
		max(__t__) OVER w AS __t__,
		first_value(__flag__) over w AS  flag
		FROM {timeline_table}
		WHERE (__t__ BETWEEN %s AND %s) AND __flag__ = 0
		window w AS (partition by rec_id ORDER BY __t__ DESC)) T
		UNION ALL
		SELECT * FROM {materialized_snapshot}
	'''.format(temp =temp_snapshot_name,
		timeline_table = 'timeline',
		latest_attributes = f_value_clause, 
		materialized_snapshot = materialized)
	print sql
	attributes = [start_timestamp,query_timestamp]
	db.command(sql,attributes)
	db.commit()

def snap_query_table_creation(snapshot_name,f_value_clause,temp_snapshot_name):
	sql = '''
	CREATE TABLE IF NOT EXISTS {new_snapshot} AS
	SELECT DISTINCT * FROM (
		SELECT rec_id,
		{latest_attributes},
		max(__t__) OVER w as __t__,
		first_value(flag) over w AS flag
		FROM {temp_snapshot}
		window w AS (partition by rec_id ORDER BY __t__ DESC)) T
	'''.format(new_snapshot = snapshot_name, 
		latest_attributes = f_value_clause, 
		temp_snapshot = temp_snapshot_name)
	db.command(sql,None)
	db.commit()

def snapshot_materialization(type,rel_name,timeline_table,query_time,materialized):
	snapshot_name,temp_snapshot_name = choose_names(type,rel_name)
	attributes = [x for x in fcn.table_attribs('rating') if not x == 'id']
	f_value_clause = create_first_value_clause(attributes)
	fcn.drop_table(temp_snapshot_name)
# 	# creates a sapshot which contains the records of materialized snapshot and the new snapshot in a temporary table
	union_snapshot_and_query(temp_snapshot_name,timeline_table,f_value_clause,query_time,materialized)
# 	# removes records that have been deleted from temporary table and creats a permenant table
	snap_query_table_creation(snapshot_name,f_value_clause,temp_snapshot_name)
# 	# drops the temporary table
	fcn.drop_table(temp_snapshot_name)

##*********************************************** BLOCKCHAIN FUNCTIONS *************************************************
def check_records_signature():
	signature_trust_check = {}
	attribs = [x for x in fcn.table_attribs('rating') if not x == 'id']
	attribs.insert(0,'rec_id')
	no_records_in_timeline = fcn.records_count('timeline')
	for id_no in range(1,no_records_in_timeline+1):
		data = fcn.fetch_specific_record_list(attribs,'timeline',"where id = '{0}'".format(id_no))
		signature_check = fcn.verify_signature(data[:9],data[9],data[8])
		signature_trust_check[data[0]] = signature_check
	return signature_trust_check

def chain_verification():
	chain_trust_check = {}
	no_records_in_timeline = fcn.records_count('timeline')
	for id_no in range(1,no_records_in_timeline):
		current_record_signature = fcn.fetch_specific_attribs_record(['signature'],'timeline',"where id = '{0}'".format(id_no))
		next_record_prev_signature= fcn.fetch_specific_attribs_record(['prev_signature'],'timeline',"where id = '{0}'".format(id_no+1))
		if current_record_signature.values() == next_record_prev_signature.values():
			chain_trust_check[str(id_no)+'_'+str(id_no+1)] = 'Trusted'
		else:
			chain_trust_check[str(id_no)+'_'+str(id_no+1)] = 'Untrusted'
	return chain_trust_check

def regular_blockchain_verification():
	untrusted_record = []
	untrusted_chain = []
	signature_check = check_records_signature()
	chain_check = chain_verification()
	for key,value in signature_check.items():
		if value == 'Untrusted':
			untrusted_record.append(key)
	for key,value in chain_check.items():
		if value == 'Untrusted':
			untrusted_chain.append(key)
	return untrusted_record, untrusted_chain

def verify_trustworthiness():
	untrusted_record, untrusted_chain = regular_blockchain_verification()
	if not (untrusted_record and untrusted_chain):
		print 'The chain is trustworthy'
	else:
		print 'The chain is broken'