from lib import functions as fcn
from lib import postgresCon as pc
from lib import keyGen as kg
from lib.config import *


def current_information():
	timeline_records =  fcn.records_count('timeline',None)
	relation_records = fcn.records_count('rating',None)
	deletion_number = fcn.records_count('timeline', 'WHERE __flag__ = 1')
	update_number = timeline_records-(relation_records+deletion_number)
	snapshot_list = fcn.fetch_table_list('snapshot')
	relation_size = fcn.table_size('rating')['size']
	timeline_size = fcn.table_size('timeline')['size']
	timeline_duration = fcn.table_duration('timeline')
	
	info_dict = {'timeline_records':timeline_records,'timeline_size' : timeline_size , 
	'relation_records':relation_records, 'relation_size': relation_size,
	'number_of_deletes':deletion_number, 'number_of_updates': update_number, 
	'snapshot_list':snapshot_list, 'timeline_duration': timeline_duration}

	return info_dict
	
def timline_records():
	records = fcn.fetch_table_records('timeline')
	keys = records[0].keys()
	# other_info = {x: '' for x in keys if x not in ['__t__','rec_id']}
	other_info_keys = [x for x in keys if x not in ['__t__','rec_id','__flag__']]
	for i in range (len(records)):
	# 	#__flag__ is a reserved firbase variable
		records_data = {'rec_id':records[i]['rec_id'], 
			'timestamp': str(records[i]['__t__']), 
			'f':records[i]['__flag__'],
			'other_info': [{x:records[i][x] for x in other_info_keys}]}
		fcn.firebase_writing(records_data,'components',str(records[i]['id']))
	# # print record_list