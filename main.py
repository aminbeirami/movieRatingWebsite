import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask, render_template, session, request, flash, redirect, url_for
from lib.config import *
from lib import functions as fcn
from functools import wraps

app = Flask(__name__)
app.secret_key = SECRET_KEY

cron = Scheduler(daemon=True)
cron.start()

P=1

@cron.interval_schedule(seconds=P)


@app.route('/')
def main():
	fcn.hello()
	return render_template('index.html')

if __name__ == '__main__':
	app.debug = True
	app.run(use_reloader=False)
