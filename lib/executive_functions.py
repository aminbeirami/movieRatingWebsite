#BY AMIN BEIRAMI -- beirami.m.a@gmail.com
#EXECUTIVE FUNCTIONS
from lib import functions as fcn
from lib import postgresCon as pc
from lib.config import *
from random import randint, randrange
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import json



#database initialization
db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)
clsuter_info = {'clusters':[],'snapshots':[]}

# **************************************************** SNAPSHOT CREATION FUNCTIONS ***************************************************************

def create_first_value_clause(attributes):
	# clause = ",\n".join("last_value({c}) over w as {c}".format(c=x) for x in attributes)
	clause = ",\n".join("last_value({c}) over (partition by rec_id order by __t__ RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as {c}".format(c=x) for x in attributes)
	return clause

def create_snapshots(rel_name,timestamp):
	snap_id = fcn.get_nextval_counter('snap_id')
	snapshot_name = "{0}__{1}".format(rel_name,str(snap_id))
	attributes = [x for x in fcn.table_attribs(rel_name) if not x == 'id']
	f_value_clause = create_first_value_clause(attributes)

	sql = '''
	 	CREATE TABLE IF NOT EXISTS {snap_name} AS 
	 	SELECT DISTINCT * FROM (
	 		SELECT
	 			rec_id,
	 			{latest_attributes},
	 			max(__t__) OVER w AS __t__,
	 			first_value(__flag__) over w AS  flag
	 		FROM {timeline_table}
	 		WHERE __t__<= %s
	 			window w AS (partition by rec_id ORDER BY __t__ DESC)) T
	 		WHERE flag =0
	 '''.format(snap_name = snapshot_name, timeline_table = 'timeline',latest_attributes = f_value_clause)

	parameters = [timestamp,]
	db.command(sql,parameters)
	db.commit()
	return snapshot_name
# ******************************************* RANDOM INSERTION,DELETION AND UPDATE fUNCTIONS *****************************************************

def random_insert(): #insrts random records to the main database
	random_rating = randint(1,5)
	user = fcn.random_user()
	movie = fcn.random_movie()
	rating_attribs = [x for x in fcn.table_attribs('rating')]
	record_id = fcn.get_nextval_counter('rating_id_seq')
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
	random_record_list = list(fcn.fetch_specific_record_list(attribs,'rating','ORDER BY RANDOM() LIMIT 1','one'))
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record_list[7]))
	try:
		sql = "DELETE FROM rating WHERE id =(%s)"
		parameters = (random_record_list[0],)
		db.command(sql,parameters)
		db.commit()
		for i in range(1,len(random_record_list)-1):
			random_record_list[i] = None
		signature = fcn.create_signature(random_record_list,random_record_list[8])
		record_id = fcn.fetch_specific_record_list(['last_value',],'id','','one')[0]
		sql = "UPDATE timeline SET signature = (%s) WHERE id = (%s)"
		parameters = [signature,record_id]
		db.command(sql,parameters)
		db.commit()
		print 'delete'
		data = {'action':'delete','user':random_record_list[8],'movie':random_record_list[2],'rating':random_record_list[6],'position':[user_location['lat'],user_location['long']],'time':str(datetime.now())}
		return data
	except Exception as e:
		print e
		return 'error'
  
def random_update():
	random_rate = randint(1,5)
	attribs = [x for x in fcn.table_attribs('rating') if not x == 'signature']
	random_record_list = list(fcn.fetch_specific_record_list(attribs,'rating','ORDER BY RANDOM() LIMIT 1','one'))
	random_record_dict = fcn.fetch_specific_attribs_record(attribs,'rating', 'WHERE id ={0}'.format(random_record_list[0]))
	random_record_list[6] = random_rate
	signature = fcn.create_signature(random_record_list,random_record_dict['username'])
	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record_dict['user_id']))
	sql = "UPDATE rating SET star = (%s), signature = (%s) WHERE id =(%s)"
	parameters = (random_rate,signature,random_record_dict['id'])
	db.command(sql,parameters)
	db.commit()
	print 'update'
	data = {'action':'update','user':random_record_dict['username'],'movie':random_record_dict['mv_name'],'rating':random_record_dict['star'],'position':[user_location['lat'],	user_location['long']],'time':datetime.now()}
	return data
# ********************************************************** SIMULATION FUNCTIONS ************************************************************

def random_rating(permission):
	action_result = None
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

def random_query_generator(number):
	fmt = '%Y-%m-%d %H:%M:%S'
	duration = fcn.table_duration('timeline')
	start = duration['min']
	end = duration['max']
	number = int(number)/10
	second_difference = fcn.calc_sec_difference(start,end)
	query_list = fcn.create_query_clusters(second_difference,10,number)
	random_dates = []
	for i in range(len(query_list)):
		date = start + dt.timedelta(seconds = query_list[i])
		random_dates.append(date)
	fcn.delete_firebase('queries')
	for i in range(len(random_dates)):
		fcn.firebase_writing({'name':'query {0}'.format(str(i)), 'timestamp': str(random_dates[i])},'queries','')
	fcn.save_query_info(random_dates)
	return random_dates

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
		position = fcn.calc_time_from_seconds(np.median(query_clusters[i]),base_date)
		snapshot_positions.append(position)
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
	return	cluster_of_queries_date,snapshot_positions,cluster_of_queries_sec

def query_clustering(queries,no_clusters):
	kmeans = KMeans(n_clusters= no_clusters, init = 'k-means++',max_iter = 300, n_init = 10, random_state = 0)
	y_kmeans = kmeans.fit_predict(queries)
	return y_kmeans, kmeans.cluster_centers_

def recommend_no_clusters(max_snapshot): #elbow method in clustering
	cost = []
	query_in_seconds = []
	queries = fcn.read_query_info()
	duration = fcn.table_duration('timeline')
	for i in range(len(queries)):
		query_in_seconds.append(fcn.calc_sec_difference(duration['min'],queries[i]))
	query_list_2D = make_query_list_2D(query_in_seconds)
	for i in range(1,max_snapshot+1):
		kmeans = KMeans(n_clusters = i, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
		y_kmeans = kmeans.fit_predict(query_list_2D)
		cost.append(kmeans.inertia_)
	fig = plt.figure()
	plt.plot(cost)
	plt.xlabel('number of snapshots')
	plt.ylabel('overall cost')
	fig.savefig('static/charts/elbow.png')

def create_clusters(query_list,number):
	query_in_seconds = []
	cluster_info_date = {}
	cluster_info_scalar = {}
	duration = fcn.table_duration('timeline')
	for i in range(len(query_list)):
		query_in_seconds.append(fcn.calc_sec_difference(duration['min'],query_list[i]))
	query_list_2D = make_query_list_2D(query_in_seconds)
	# recommended = recommend_no_clusters(10) #elbow method to find the optimal snapshot numbers
	clustered_list,centroids = query_clustering(query_list_2D,number)
	query_clusters_date,snapshots_date, query_clusters_seconds = fetch_clustered_info(query_list_2D,clustered_list,number,duration['min'])
	cluster_info_date['clusters_date'] = query_clusters_date
	cluster_info_date['snapshots_date'] = snapshots_date
	cluster_info_date['base_date'] = duration['min']
	for i in range(len(centroids)):
		cluster_info_scalar[centroids[i][0]] = query_clusters_seconds[i]
	return cluster_info_date,cluster_info_scalar

#*********************************************** SNAPSHOT MATERIALIZATION FUNCTIONS *************************************************

def choose_names(operation,rel_name):
	if operation == 'query':
		query_id = fcn.get_nextval_counter('query_id')
		snapshot_name = 'query__{0}'.format(query_id)
		temp_snapshot_name = 'temp__{0}'.format(query_id)
	elif operation == 'snapshot':
		snap_id = fcn.get_nextval_counter('snap_id')
		snapshot_name = "{0}__{1}".format(rel_name,str(snap_id))
		temp_snapshot_name = "temp_{0}__{1}".format(rel_name,str(snap_id))
	else:
		print 'invalid request'
	return snapshot_name,temp_snapshot_name


def union_snapshot_and_query(temp_snapshot_name,timeline_table,f_value_clause,query_timestamp,materializing_snapshot):
	start_timestamp = fcn.table_duration(materializing_snapshot)['max']
	materialized_attribs = fcn.table_attribs(materializing_snapshot)
	snap_attribs = ",\n".join("{c}".format(c=x) for x in materialized_attribs if not (x == 'signer' or x =='snap_sign'))
	sql = '''
	CREATE TABLE IF NOT EXISTS {temp} AS
	SELECT DISTINCT * FROM (
		SELECT rec_id,
		{latest_attributes},
		max(__t__) OVER w AS __t__,
		first_value(__flag__) over w AS  flag
		FROM {timeline_table}
		WHERE (__t__ BETWEEN %s AND %s)
		window w AS (partition by rec_id ORDER BY __t__ DESC)) T
		UNION ALL
		SELECT {snapshot_attributes} FROM {materialized_snapshot}
	'''.format(temp =temp_snapshot_name,
		timeline_table = 'timeline',
		latest_attributes = f_value_clause,
		snapshot_attributes = snap_attribs,
		materialized_snapshot = materializing_snapshot)
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
		WHERE flag = 0
	'''.format(new_snapshot = snapshot_name, 
		latest_attributes = f_value_clause, 
		temp_snapshot = temp_snapshot_name)
	db.command(sql,None)
	db.commit()

def snapshot_materialization(operation,rel_name,timeline_table,query_time,materialized):
	snapshot_name,temp_snapshot_name = choose_names(operation,rel_name)
	attributes = [x for x in fcn.table_attribs('rating') if not x == 'id']
	f_value_clause = create_first_value_clause(attributes)
	fcn.drop_table(temp_snapshot_name)
# 	# creates a sapshot which contains the records of materialized snapshot and the new snapshot in a temporary table
	union_snapshot_and_query(temp_snapshot_name,timeline_table,f_value_clause,query_time,materialized)
# 	# removes records that have been deleted from temporary table and creats a permenant table
	snap_query_table_creation(snapshot_name,f_value_clause,temp_snapshot_name)
# 	# drops the temporary table
	fcn.drop_table(temp_snapshot_name)
	return snapshot_name

##*********************************************** BLOCKCHAIN FUNCTIONS *************************************************
def snapshot_signing(snapshot_name,user):
	sql ='''
			SELECT user_id, role, 
			CASE WHEN role = 1 
			THEN 'yes' ELSE 'no' 
			END AS is_admin FROM users WHERE username = '{username}'
		'''.format(username = user)
	user_info = db.query(sql,None,'one')
	if user_info[2] =='yes':
		snap_data = fcn.fetch_snapshot_records(snapshot_name)
		snap_signature = fcn.create_signature(snap_data,user)
		fcn.add_columns_snapshot(snapshot_name)
		fcn.insert_snapshot_signature(snapshot_name,user,snap_signature)
		return 1
	else:
		print 'not a privileged user'
		return 0

def snapshot_creation_operation(materialized_snapshot,optimal_timestamp,interval):
	chain_trustworthiness = fcn.verify_trustworthiness(interval[0],interval[1])
	if materialized_snapshot:
		snapshot_trustworthiness = fcn.verify_snapshot_signature(materialized_snapshot)
		if snapshot_trustworthiness == 'Trusted':
			if chain_trustworthiness == 'Trusted':
				resulted_snapshot = snapshot_materialization('snapshot','rating','timeline',optimal_timestamp,materialized_snapshot)
				status = snapshot_signing(resulted_snapshot,'admin')
				if status ==1:
					print 'signing snapshot {snap_name} was successful'.format(snap_name = resulted_snapshot)
					return resulted_snapshot
				else:
					print 'signing snapshot {snap_name} was unsuccessful! please check the log.'.format(snap_name = snapshot_name)
					return 0
			else:
				print 'Blockchain untrusted. Please check the log file.'
				return -1
		else:
			print 'Snapshot signature does not match. Please check the log file.'
			return -2
	else:
		if chain_trustworthiness == 'Trusted':
			resulted_snapshot = create_snapshots('rating',optimal_timestamp)
			status = snapshot_signing(resulted_snapshot,'admin')
			if status ==1:
				print 'signing snapshot {snap_name} was successful'.format(snap_name = resulted_snapshot)
				return resulted_snapshot
			else:
				print 'signing snapshot {snap_name} was unsuccessful! please check the log.'.format(snap_name = snapshot_name)
				return 0
		else:
			print 'untrusted blockchain! please check the log.'
			return -1
##*********************************************** snapshot generation and query ***************************************
def K_nearest_preprocessing(query,clusters):
	all_queries = []
	classes = []
	class_names = []
	fmt = '%Y-%m-%d %H:%M:%S.%f'
	query_datetime = datetime.strptime(query, fmt)
	base_datetime = datetime.strptime(clusters[0].values()[0][1],fmt)
	query_sec = fcn.calc_sec_difference(base_datetime,query_datetime)
	for i in range(len(clusters)):
		class_names.append(clusters[i].keys()[0])
		for j in range(len(clusters[i].values()[0][0])):
			all_queries.append([float(clusters[i].values()[0][0][j])])
			classes.append(i)
	return all_queries, classes,class_names, query_sec

def query_K_nearest(query, clusters):
	all_queries, classes, class_names, query_sec = K_nearest_preprocessing(query,clusters)
	neigh = KNeighborsClassifier(n_neighbors=3)
	neigh.fit(all_queries, classes)
	predicted_class = neigh.predict(query_sec)[0]
	return class_names[predicted_class]

def prepare_and_save_firebase(clustering_info,snapshot_names):
	fcn.delete_firebase('snapshots')
	for i in range(len(snapshot_names)):
		print {'name':snapshot_names[i], 'timestamp': str(clustering_info['snapshots_date'][i])}
		fcn.firebase_writing({'name':snapshot_names[i], 'timestamp': str(clustering_info['snapshots_date'][i])},'snapshots', '')

def optimal_trusted_snapshot_generation(number):
	generated_snapshots = []
	queries = fcn.read_query_info()
	clustering_info,snapshot_info = create_clusters(queries, number)
	optimal_snapshots = clustering_info['snapshots_date']
	intervals = fcn.generate_verification_intervals(optimal_snapshots)
	optimal_snapshots.pop(0)

	if len(optimal_snapshots)==1:
		resulted_snapshot = snapshot_creation_operation(None,optimal_snapshots[0],intervals[0])
		generated_snapshots.append(resulted_snapshot)
	else:
		resulted_snapshot = snapshot_creation_operation(None,optimal_snapshots[0],intervals[0])
		generated_snapshots.append(resulted_snapshot)
		for i in range(1,len(optimal_snapshots)):
			resulted_snapshot = snapshot_creation_operation(generated_snapshots[i-1],optimal_snapshots[i],intervals[i])
			generated_snapshots.append(resulted_snapshot)

	fcn.delete_snapshot_info()
	fcn.save_snapshot_info(snapshot_info,clustering_info,generated_snapshots)
	# for i in range(len(snapshot_info)):
	# 	print str(clustering_info['snapshots_date'][i])
	prepare_and_save_firebase(clustering_info, generated_snapshots)
	return generated_snapshots

def choose_snapshot_materialization(query_timestamp):
	selected_snapshot = None
	snap_info,clusters_boundary = fcn.import_snapshot_info()
	snapshots = clusters_boundary.keys()
	for i in range(len(snapshots)):
		if clusters_boundary[snapshots[i]][0] <= query_timestamp <= clusters_boundary[snapshots[i]][1]:
			selected_snapshot = snapshots[i]
	if selected_snapshot == None:	
		selected_snapshot = query_K_nearest(query_timestamp,snap_info)
	return selected_snapshot

def run_query(query_timestamp):
	operation = 'query'
	rel_name = 'rating'
	timeline_table = 'timeline'
	query_time = query_timestamp
	materialized = choose_snapshot_materialization(query_timestamp)
	snapshot_materialization(operation,rel_name,timeline_table,query_time,materialized)
	fcn.firebase_writing({'query':query_timestamp, 'materialized':materialized},'individual_query','')

def query_snapshot(snapshot_name):
	dict = {}
	dict_list = []
	data = fcn.fetch_table_records(snapshot_name)
	keys = fcn.table_attribs(snapshot_name)
	integerKeys = ['mov_id','rec_id','star','user_id','release_date']
	forbiddenKeys = ['flag','__t__' ,'signer', 'snap_sign']
	keys = [x for x in keys if x not in integerKeys+forbiddenKeys]
	for i in range(len(data)):
		temp_dict = {x :data[i][x] for x in keys}
		for integers in integerKeys:
			temp_dict[integers] = str(data[i][integers])
		dict_list.append(temp_dict)
	dict['name'] = snapshot_name
	dict['data'] = dict_list
	dict['status'] = fcn.verify_snapshot_signature(snapshot_name)
	dict['keys'] = keys+integerKeys
	fcn.firebase_writing(dict,'snapshotQuery','snapshot')

def verify_trust():
	duration = fcn.table_duration('timeline')
	status = fcn.verify_trustworthiness(duration['min'],duration['max'])
	print status