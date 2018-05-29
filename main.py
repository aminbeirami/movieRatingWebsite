import atexit
import dash
import flask
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input,Output,State
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from functools import wraps


server = flask.Flask(__name__)

@server.route('/', methods= ['POST','GET'])
def main():
	# app.layout = html.Div(['This is the outermost Div'])
	return render_template('index.html')

app = dash.Dash(__name__, server=server, url_base_app = '/dash')
server.secret_key = SECRET_KEY

json_list = []
table_size = []
cron = Scheduler(daemon=True)
cron.start()
P=1

#-------------------------------------- Dash -------------------------------------------------------
app.layout= html.Div([
 html.H4("Hello I'm a Dash app"),
    html.Div(id='target'),
    dcc.Input(id='input', type='text', value=''),
    html.Button(id='submit', n_clicks=0, children='Save')
])

@app.callback(Output('target', 'children'), [Input('submit', 'n_clicks')],
              [State('input', 'value')])
def callback(n_clicks, state):
	size = fcn.table_size()
	print size
	return "callback received value: {}".format(state)

#-------------------------------------- Flask-------------------------------------------------------

# @cron.interval_schedule(seconds=P)
@server.route('/actions', methods = ['POST','GET'])
def actions_json():
	list_len = len(json_list)
	if list_len <=10:
		json_list.insert(0,ex.random_rating(True))
	else:
		json_list.pop(10)
		json_list.insert(0,ex.random_rating(True))
	print json_list
	print len(json_list)
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
