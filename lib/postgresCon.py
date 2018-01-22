import psycopg2 as pg
import functools
import os
from lib.config import *

def catch_exception(f):
	@functools.wraps(f)
	def func(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			if f.__name__=="__init__":
				print "The database is unreachable."
				return None
			else:
				print e
				# print "There is an error in the query syntax."
				return None
	return func

class DataBase:
	# @catch_exception
	def __init__(self,SERVER,USERNAME,PASSWORD,DATABASE):
		self.__setting = "dbname= " + DATABASE+ " user= " + USERNAME + " host=" + SERVER + " password="+ PASSWORD
		self.__conn = pg.connect(self.__setting)
		self.__cursor = self.__conn.cursor()

	def __enter__(self):
		return DataBase()
		
	# @catch_exception
	def query(self, sql, arguments,fetch):
		if arguments:
			self.__cursor.execute(sql,arguments)
		else:
			self.__cursor.execute(sql)
		if fetch == 'one':
			return self.__cursor.fetchone()
		else:
			return self.__cursor.fetchall()
	# @catch_exception
	def command(self,sql,arguments):
		if arguments:
			self.__cursor.execute(sql,arguments)
		else:
			self.__cursor.execute(sql)
	# @catch_exception
	def insert(self,sql,arguments):
		self.__cursor.execute(sql,arguments)

	def commit(self):
		self.__conn.commit()

	def __exit__(self,exc_type, exc_val, exc_tb):
		if self.__conn:
			self.__conn.close()
