import atexit
# import dash
# import plotly.plotly as py
# import dash_html_components as html
# import dash_core_components as dcc
# import plotly.graph_objs as go
# from dash.dependencies import Input,Output,State, Event
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from functools import wraps
from collections import deque


app = Flask(__name__)
@app.route('/', methods= ['POST','GET'])
def main():
	# ex.random_insert()
	# ex.check_records_signature()
	# ex.verify_trustworthiness()
	# ex.random_delete()
	# init.init_everything()
	rel_name = 'rating'
	# ex.create_snapshots(rel_name,'2018-10-10 10:57:10.719324')
	# queries = ex.random_query_generator()
	# ex.create_snapshots('rating','2018-05-24')
	# query_number = ex.snapshot_materialization()
	ex.snapshot_materialization('snapshot',rel_name,'timeline','2018-10-10 10:58:10.719324','rating__86')
	return render_template('index.html')

app.secret_key = SECRET_KEY

db_size = deque(maxlen = 20)
time_size_checked = deque(maxlen = 20)

json_list = []
current_user = {'username':'0','location' : ['0','0']}

cron = Scheduler(daemon=True)
cron.start()
P=1
# Scheduler.add_job(ex.random_rating(False), 'interval', seconds=1, id='my_job_id')

#-------------------------------------- Python Dash -------------------------------------------------------
# app = dash.Dash(__name__, server=server, url_base_app = '/dash')

# #*********LIVE GRAPH USING DASH*****************
# # dash_x = deque(maxlen = 20)
# # dash_y = deque(maxlen = 20)
# # dash_x.append(1)

# app.layout= html.Div([
# 	dcc.Graph(id='live-graph', animate=True),
# 	dcc.Interval(
# 		id = 'graph-update',
# 		interval = 50000
# 		)
# ])

#***********LIVE MAP USING DASH***************
# @app.callback(Output('live-graph','figure'),events = [Event('graph-update','interval')])
# def dash_map():
# 	global current_user
# 	latitude = 45
# 	longitude = -73
	
# 	data = [ go.Scattermapbox(
#         lat=[latitude],
#         lon=[longitude],
#         mode='markers',
#         marker=dict(
#             size=14
#         ),
#         text=[current_user['username']],
#     )]
# 	layout = go.Layout(
# 	    autosize=True,
# 	    hovermode='closest',
# 	    mapbox=dict(
# 	        accesstoken='pk.eyJ1IjoiYW1pbmJlaXJhbWkiLCJhIjoiY2poc2N3MmxmMDFtYjN2cnducDY1cTh4ZiJ9.IWbzbZm_waJI--kxP0bLXw',
# 	        bearing=0,
# 	        center=dict(
# 	            lat=45,
# 	            lon=-73
# 	        ),
# 	        pitch=0,
# 	        zoom=5
# 	    ),)
# 	return {'data':[data],'layout':layout}


#-------------------------------------- Flask-------------------------------------------------------

# @cron.interval_schedule(seconds=P)
# @app.route('/actions', methods = ['POST','GET'])
# def actions_json():
# 	list_len = len(json_list)
# 	if list_len <=10:
# 		json_list.insert(0,ex.random_rating(True))
# 		current_user['username'] = json_list[0]['user']
# 		current_user['position']=json_list[0]['position']
# 	else:
# 		json_list.pop(10)
# 		json_list.insert(0,ex.random_rating(True))
# 		current_user['username'] = json_list[0]['user']
# 		current_user['position']=json_list[0]['position']

# 	print fcn.table_size()
# 	return jsonify((json_list))
@cron.interval_schedule(seconds =P)
@app.route('/init')
def initialization():
	# ex.random_rating(True)
	# init.drop_tables()
	# init.drop_function()
	# init.create_table()
	# init.db_function()
	# init.create_snapshot_sequence()
	return render_template('base.html')

@app.route('/action_table')
def action_table():
	return render_template('table.html')



if __name__ == '__main__':
	app.debug = True
	app.run(use_reloader=False)
