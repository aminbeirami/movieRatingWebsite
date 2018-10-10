# def random_update():
# 	random_rate = randint(1,5)
# 	attribs = [x for x in fcn.table_attribs('rating') if not x == 'signature']
# 	random_record_list = list(fcn.fetch_specific_record_list(attribs,'rating','ORDER BY RANDOM() LIMIT 1'))
# 	random_record_dict = fcn.fetch_specific_attribs_record(attribs,'rating', 'WHERE id ={0}'.format(random_record_list[0]))
# 	random_record_list[6] = random_rate
# 	signature = fcn.create_signature(random_record_list,random_record_dict['username'])
# 	user_location = fcn.fetch_specific_attribs_record(['lat','long'],'users','where user_id = {0}'.format(random_record_dict['user_id']))
# 	sql = "UPDATE rating SET star = (%s), signature = (%s) WHERE id =(%s)"
# 	parameters = (random_rate,signature,random_record_dict['id'])
# 	db.command(sql,parameters)
# 	db.commit()
# 	print 'update'
# 	return {'action':'update',\
# 	'user':random_record_dict['username'],\
# 	'movie':random_record_dict['mv_name'],\
# 	'rating':random_record_dict['star'],\
# 	'position':[user_location['lat'],\
# 	user_location['long']],
# 	'time':datetime.now()}