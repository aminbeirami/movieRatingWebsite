import atexit
import dash
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from functools import wraps

server = Flask(__name__)
server.secret_key = SECRET_KEY
app = dash.Dash()

json_list = []
cron = Scheduler(daemon=True)
cron.start()
P=1

@server.route('/', methods= ['POST','GET'])
def main():
	return render_template('index.html')

@cron.interval_schedule(seconds=P)
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
	# init.drop_tables()
	# init.drop_function()
	# init.create_table()
	# init.db_function()
	ex.random_rating(True)
	return render_template('base.html')









if __name__ == '__main__':
	server.debug = True
	server.run(use_reloader=False)
