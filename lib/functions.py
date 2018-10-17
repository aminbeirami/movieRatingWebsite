# BY AMIN BEIRAMI -- REGULAR FUNCTIONS
from lib import postgresCon as pc
import functools
from lib import keyGen as kg
from random import randint
from lib.config import *
from time import sleep
from datetime import datetime,timedelta
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

def drop_table(name):
	sql = 'DROP TABLE IF EXISTS {0}'.format(name)
	db.command(sql,None)
	db.commit()
	print 'table {0} was dropped!'.format(name)

def get_nextval_counter(countername):
	sql = "SELECT NEXTVAL('{0}')".format(countername)
	result = db.query(sql,None,'one')
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

def fetch_everything_record_dict(table_name,condition):
	sql = "SELECT * FROM {0} {1}".format(table_name,condition)
	rec_data = db.query(sql,None,'one')
	rec_attribs = table_attribs(table_name)
	rec_dictionary = make_dict(rec_attribs,rec_data)
	return rec_dictionary

def fetch_snapshot_records(snapshot_name):
	snapshot_attribs = table_attribs(snapshot_name)
	select_attribs = ",".join("{c}".format(c=x) for x in snapshot_attribs if not (x =='snap_sign' or x == 'signer'))
	sql = "SELECT {attributes} FROM {snap_name}".format(attributes = select_attribs,snap_name = snapshot_name)
	rec_data = db.query(sql,None,'all')
	return rec_data

def fetch_specific_attribs_record(attribs,table_name,condition):
	result = {}
	rec_dictionary = fetch_everything_record_dict(table_name,condition)
	for i in attribs:
		result[i]=rec_dictionary[i]
	return result

def fetch_specific_record_list(attribs,table_name,condition,number):
	attribs = ','.join(attribs)
	sql = "SELECT {0} FROM {1} {2}".format(attribs,table_name,condition)
	result = db.query(sql,None,number)
	return result

def records_count(table_name,condition): # returns number of movies in the database
	sql = "SELECT COUNT(*) FROM {table} {condition}".format(table = table_name, condition = condition)
	result = db.query(sql,None,"one")
	return result[0]

def define_user(username,latitude,longitude,role):
	isadmin = 1 if role == 'admin' else 0
	user_attribs = [x for x in table_attribs('users')]
	user_id = get_nextval_counter('user_id')
	sql = "INSERT INTO users VALUES (%s)"%",".join("%s" for i in range(len(user_attribs)))
	keyGen = kg.RSAEncryption()
	pub_key,priv_key = keyGen.generate_keys()
	parameters = [user_id,username,priv_key,pub_key,latitude,longitude,isadmin]
	db.insert(sql,parameters)
	db.commit()
	print 'The user {0} with {1} role added to the database'.format(username,role)

def random_user(): #chooses a random user from database
	user_id = randint(0,records_count('users',None))
	user_data = fetch_everything_record_dict('users','where user_id = {0}'.format(user_id))
	return user_data 

def random_movie(): #chooses a random movie name from database
	movie_id = randint(0,records_count('movies',None))
	movie_data = fetch_everything_record_dict('movies','where mov_id = {0}'.format(movie_id))
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
	data = ''.join([str(x) for x in raw_parameters])
	keyGen = kg.RSAEncryption()
	signature = keyGen.generate_signature(data,key['private_key'])
	return signature

def verify_signature(raw_parameters,signature,username):
	key = fetch_specific_attribs_record(['public_key',], 'users',"where username = '{0}'".format(username))
	data = ''.join([str(x) for x in raw_parameters])
	keyGen = kg.RSAEncryption()
	result = keyGen.verifying_signature(data,signature,key['public_key'])
	return result

def table_size():
	sql = "select pg_relation_size('rating');"
	result = db.query(sql,None,'one')
	return {'size': int(result[0]),'time_checked':datetime.now()}

def table_duration(table_name):
	sql = "SELECT MAX(__t__) FROM {0}".format(table_name)
	max_date = db.query(sql,None,'one')[0]
	sql = "SELECT MIN(__t__) FROM {0}".format(table_name)
	min_date = db.query(sql,None,'one')[0]
	return {'min': min_date, 'max':max_date}

def calc_sec_difference(base_date, query_date):
	second_difference = int((query_date-base_date).total_seconds())
	return second_difference

def calc_time_from_seconds(query_seconds,base_date):
	return base_date + timedelta(seconds = query_seconds)

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
	return sorted(query_list)

def select_records_ids(timeline_name, start_timestamp, end_timestamp):
	condition = "WHERE __t__ BETWEEN '{start}' AND '{end}'".format(start = start_timestamp, end = end_timestamp)
	attribs = ['id',]
	result = fetch_specific_record_list(attribs,timeline_name,condition,'all')
	return result

def check_records_signature(start_timestamp, end_timestamp):
	signature_trust_check = {}
	attribs = [x for x in table_attribs('rating') if not x == 'id']
	attribs.insert(0,'rec_id')
	list_of_ids = select_records_ids('timeline',start_timestamp,end_timestamp)
	for id_no in list_of_ids:
		data = fetch_specific_record_list(attribs,'timeline',"where id = '{0}'".format(id_no[0]),'one')
		signature_check = verify_signature(data[:9],data[9],data[8])
		signature_trust_check[id_no[0]] = signature_check
	print signature_trust_check
	return signature_trust_check

def chain_verification(start_timestamp,end_timestamp):
	chain_trust_check = {}
	list_of_ids = select_records_ids('timeline',start_timestamp,end_timestamp)
	for id_no in list_of_ids:
		current_record_signature = fetch_specific_attribs_record(['signature'],'timeline',"where id = '{0}'".format(id_no[0]))
		next_record_prev_signature= fetch_specific_attribs_record(['prev_signature'],'timeline',"where id = '{0}'".format(id_no[0]+1))
		if next_record_prev_signature:
			if current_record_signature.values() == next_record_prev_signature.values():
				chain_trust_check[str(id_no[0])+'_'+str(id_no[0]+1)] = 'Trusted'
			else:
				chain_trust_check[str(id_no[0])+'_'+str(id_no[0]+1)] = 'Untrusted'
	return chain_trust_check

def regular_blockchain_verification(start_timestamp,end_timestamp):
	untrusted_record = []
	untrusted_chain = []
	signature_check = check_records_signature(start_timestamp,end_timestamp)
	chain_check = chain_verification(start_timestamp,end_timestamp)
	for key,value in signature_check.items():
		if value == 'Untrusted':
			untrusted_record.append(key)
	for key,value in chain_check.items():
		if value == 'Untrusted':
			untrusted_chain.append(key)
	return untrusted_record, untrusted_chain

def verify_trustworthiness(start_timestamp,end_timestamp):
	untrusted_record, untrusted_chain = regular_blockchain_verification(start_timestamp,end_timestamp)
	if not (untrusted_record and untrusted_chain):
		print 'The chain is trustworthy'
		return 1
	else:
		print 'The chain is broken'
		return 0

def add_columns_snapshot(snapshot_name):
	sql = '''
			ALTER TABLE {snap_name} 
			ADD COLUMN signer TEXT, 
			ADD COLUMN snap_sign TEXT
		'''.format(snap_name = snapshot_name)
	db.command(sql,None)
	db.commit()

def insert_snapshot_signature(snapshot_name,signer,signature):
	sql = "INSERT INTO {snap_name} (signer, snap_sign) VALUES (%s, %s)".format(snap_name = snapshot_name)
	parameters = [signer,signature]
	db.insert(sql,parameters)
	db.commit()
	print 'done'

def fetch_snapshot_signature(snapshot_name):
	attribs = ['signer', 'snap_sign']
	condition = "WHERE snap_sign IS NOT NULL"
	result = fetch_specific_attribs_record(attribs,snapshot_name,condition)
	return result['signer'], result['snap_sign']