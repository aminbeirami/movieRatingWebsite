import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from functools import wraps

app = Flask(__name__)
app.secret_key = SECRET_KEY
json_list = []

@app.route('/', methods= ['POST','GET'])
def main():
	return render_template('index.html')


@app.route('/actions', methods = ['POST','GET'])
def actions_json():
	list_len = len(json_list)
	if list_len <=10:
		json_list.append (ex.random_rating(True))
	else:
		json_list.pop(0)
		json_list.append(ex.random_rating(True))
	print json_list
	return jsonify(json_list)


	

@app.route('/init')
def initialization():
	# init.drop_tables()
	# init.drop_function()
	# init.create_table()
	# init.db_function()
	ex.random_rating(True)
	return render_template('base.html')









if __name__ == '__main__':
	app.debug = True
	app.run(use_reloader=False)
