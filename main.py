import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for
from lib.config import *
from lib import functions as fcn
from lib import initialization as init
from functools import wraps

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def main():
	# fcn.random_rating()
	# init.drop_tables()
	# init.drop_function()
	# init.create_database()
	init.db_function()
	return render_template('index.html')

if __name__ == '__main__':
	app.debug = True
	app.run(use_reloader=False)
