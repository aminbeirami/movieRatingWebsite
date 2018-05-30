import atexit
import dash
import flask
import plotly.plotly as py
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from dash.dependencies import Input,Output,State, Event
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from functools import wraps
from collections import deque


server = flask.Flask(__name__)

@server.route('/', methods= ['POST','GET'])
def main():
	# app.layout = html.Div(['This is the outermost Div'])
	return render_template('index.html')

server.secret_key = SECRET_KEY

json_list = []

cron = Scheduler(daemon=True)
cron.start()
P=10

#-------------------------------------- Dash -------------------------------------------------------
app = dash.Dash(__name__, server=server, url_base_app = '/dash')
current_user = {}
#*********LIVE GRAPH USING DASH*****************
# dash_x = deque(maxlen = 20)
# dash_y = deque(maxlen = 20)
# dash_x.append(1)


layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        bearing=0,
        center=dict(
            lat=45,
            lon=-73
        ),
        pitch=0,
        zoom=5
    ),
)



app.layout= html.Div([
	dcc.Graph(id='live-graph', animate=True),
	dcc.Interval(
		id = 'graph-update',
		interval = 5000
		)
])

# @app.callback(Output('live-graph', 'figure'),
# 	events = [Event('graph-update','interval')])
# def dash_graph():
# 	global dash_x
# 	global dash_y
# 	table_size = fcn.table_size()
# 	dash_x.append(dash_x[-1]+1)
# 	dash_y.append(table_size)

# 	data = go.Scatter(
# 		x = list(dash_x),
# 		y = list((dash_y)),
# 		name = 'DB size',
# 		mode = 'lines+markers'
# 		)
# 	return {'data':[data], 'layout': go.Layout(xaxis = dict(range = [min(dash_x),max(dash_x)]),
# 												yaxis = dict(range = [min(dash_y)-0.001,max(dash_y)+0.001]))}

#***********LIVE MAP USING DASH***************
@app.callback(Output('live-graph','figure'),events = [Event('graph-update','interval')])
def dash_map():
	global current_user
	
	data = [ go.Scattermapbox(
        lat=[current_user['location'][0]],
        lon=[current_user['location'][1]],
        mode='markers',
        marker=dict(
            size=14
        ),
        text=[current_user['username']],
    )]
	layout = go.Layout(
	    autosize=True,
	    hovermode='closest',
	    mapbox=dict(
	        accesstoken=mapbox_access_token,
	        bearing=0,
	        center=dict(
	            lat=45,
	            lon=-73
	        ),
	        pitch=0,
	        zoom=5
	    ),)
	return {'data':[data],'layout':layout}


#-------------------------------------- Flask-------------------------------------------------------

@cron.interval_schedule(seconds=P)
@server.route('/actions', methods = ['POST','GET'])
def actions_json():
	list_len = len(json_list)
	if list_len <=10:
		json_list.insert(0,ex.random_rating(True))
		current_user={'username':json_list[0]['user'],'location':json_list[0]['position']}
	else:
		json_list.pop(10)
		json_list.insert(0,ex.random_rating(True))
		current_user={'username':json_list[0]['user'],'location':json_list[0]['position']}

	print current_user
	return jsonify((json_list))

@server.route('/init')
def initialization():
	init.drop_tables()
	init.drop_function()
	init.create_table()
	init.db_function()
	return render_template('base.html')



if __name__ == '__main__':
	server.debug = True
	server.run(use_reloader=False)
