import atexit, json, time, threading, logging
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for,jsonify,make_response
from lib.config import *
from random import randint
from lib import functions as fcn
from lib import initialization as init
from lib import executive_functions as ex
from lib import info
from functools import wraps
from collections import deque


app = Flask(__name__)
app.secret_key = SECRET_KEY

logging.basicConfig()
cron = Scheduler(daemon=True)

@cron.interval_schedule(seconds =2)
def random_data():
	action = None
	random_no = randint(1,2)
	if random_no ==1:
		action = ex.random_rating(True)
	else:	
		action = ex.random_rating(False)
	fcn.firebase_writing(action,'activity',None)
	info.timline_records()


#random record generation


@app.route('/', methods= ['POST','GET'])
def main():
	if request.method == 'POST':
		if request.form['submit_button'] == 'generate-random':
			cron.start()
		if request.form['submit_button'] == 'stop-random':
			cron.shutdown(wait=False)
		if request.form['submit_button'] == 'random-query':
			number = request.form['number']
			ex.random_query_generator(number)
		if request.form['submit_button'] == 'snapshot':
			number = int(request.form['snap_number'])
			ex.optimal_trusted_snapshot_generation(number)
		if request.form['submit_button'] == 'view-snapshot':
			ex.query_snapshot(request.form['snapshot-name'])
		if request.form['submit_button'] == 'analyze-snapshots':
			number = int(request.form['snapshot-numbers'])
			ex.recommend_no_clusters(number)
		if request.form['submit_button'] == 'trust-checker':
			ex.verify_trust()
		return redirect(url_for('main'))
	else:
		return render_template('index.html')


db_size = deque(maxlen = 20)
time_size_checked = deque(maxlen = 20)

json_list = []
current_user = {'username':'0','location' : ['0','0']}



@app.route('/init', methods= ['POST','GET'])
def db_information():
	if request.method == 'POST':
		if request.form['submit_button'] == 'refresh':
			db_information = info.current_information()
			fcn.firebase_writing(db_information,'info','init_information')
		elif request.form['submit_button'] == 'clean':
			init.init_everything()
		return redirect(url_for('db_information'))
	elif request.method == 'GET':
		return render_template('init.html')

@app.route('/test', methods= ['POST','GET'])
def test_data():
	data = []
	if request.method == 'POST':
		if request.form['submit_button'] == 'Do Something':
			data.append('amin')
		elif request.form['submit_button'] == 'Do Something Else':
			data.append('zahra')
		else:
			data.append('nothing')
		print data
		return redirect(url_for('test_data'))
	elif request.method == 'GET':
		init.init_everything()
		return render_template('test.html',data = data)

@app.route('/delete')
def delete_everything():
	init.init_everything()
	return render_template('index.html')

@app.route('/action_table')
def action_table():
	return render_template('table.html')

if __name__ == '__main__':
	app.debug = True
	app.run(use_reloader=False)
