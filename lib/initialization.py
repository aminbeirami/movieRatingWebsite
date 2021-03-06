from lib import postgresCon as pc
from lib.config import *
from lib import functions as fcn
import os
db = pc.DataBase(SERVER,USERNAME,PASSWORD,DATABASE)

def db_function(): #turns on the triggers. if there are no triggers, it generates the triggers.
	sql = '''
		CREATE FUNCTION log_data()
		RETURNS TRIGGER
		LANGUAGE PLPGSQL
		AS
		$$
		BEGIN
		    IF (TG_OP = 'DELETE') THEN
		        INSERT INTO timeline
		        SELECT NEXTVAL('id'), OLD.id, NULL, NULL, NULL, NULL, NULL, NULL, NULL,OLD.username,NULL,(SELECT signature FROM timeline WHERE id = (SELECT last_value-1 FROM id)),1,NOW();
		        RETURN OLD;
		    ELSIF (TG_OP = 'UPDATE') THEN
		        INSERT INTO timeline 
		        SELECT NEXTVAL('id'), NEW.id, NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,(SELECT signature FROM timeline WHERE id = (SELECT last_value-1 FROM id)),0,NOW();
		        RETURN NEW;
		    ELSIF (TG_OP = 'INSERT') THEN
		        INSERT INTO timeline
		        SELECT NEXTVAL('id'), NEW.id , NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,(SELECT signature FROM timeline WHERE id = (SELECT last_value-1 FROM id)),0,NOW();
		        RETURN NEW;
		    END IF;
		    RETURN NULL;
		END;
		$$;
		'''
	db.command(sql,None)
	db.commit()

	sql = '''CREATE TRIGGER base_data_log
		AFTER INSERT OR UPDATE OR DELETE ON rating
		FOR EACH ROW EXECUTE PROCEDURE log_data()
		'''
	db.command(sql,None)
	db.commit()
	print '--- relevant triggers created'

def drop_tables():
	sql = "DROP TABLE IF EXISTS rating"
	db.command(sql,None)
	db.commit()

def drop_function():
	sql = "DROP FUNCTION IF EXISTS log_data()"
	db.command(sql,None)
	db.commit()

def create_table(): 
	sql = '''CREATE TABLE IF NOT EXISTS 
  	rating (id SERIAL,
	mov_id INT,
	mv_name TEXT,
	mv_year TEXT,
	release_date TIMESTAMP,
	movie_url TEXT,
	star INT,
	user_id INT,
	username TEXT,
	signature TEXT )'''
  	db.command(sql,None)
  	db.commit()
  	print '--- relevant databases created successfully!'

def create_snapshot_sequence():
	sql = "CREATE SEQUENCE IF NOT EXISTS snap_id"
	db.command(sql,None)
	sql2 = "CREATE SEQUENCE IF NOT EXISTS query_id"
	db.command(sql2,None)
	db.commit()
	print 'the sanp_id and query_id sequences created.'

def reset_ids(id_name):
	sql = "ALTER SEQUENCE {0} RESTART WITH 1".format(id_name)
	db.command(sql,None)
	print 'the id {0} is reseted.'.format(id_name)

def create_timeline():
	sql = ''' CREATE TABLE IF NOT EXISTS
	timeline (id SERIAL PRIMARY KEY,
	rec_id INT,
	mov_id INT,
	mv_name TEXT,
	mv_year TEXT,
	release_date TIMESTAMP,
	movie_url TEXT,
	star INT,
	user_id INT,
	username TEXT,
	signature TEXT,
	prev_signature TEXT,
	__flag__ INT,
	__t__ TIMESTAMP
	)'''
	db.command(sql,None)
	db.commit()

def drop_timeline():
	sql = "DROP TABLE IF EXISTS timeline"
	db.command(sql,None)
	db.commit()

def drop_snapshots():
	snapshots = fcn.fetch_table_list('snapshot')
	if snapshots:
		clause = ",".join("{c}".format(c=x) for x in snapshots)
		sql = 'DROP TABLE IF EXISTS {0}'.format(clause)
		db.command(sql,None)
		db.commit()
	else:
		return 0


def drop_queries():
	queries = fcn.fetch_table_list('query')
	if queries:
		clause = ",".join("{c}".format(c=x) for x in queries)
		sql = 'DROP TABLE IF EXISTS {0}'.format(clause)
		db.command(sql,None)
		db.commit()
	else:
		return 0
def init_everything():
	"--- started initialization..."
	drop_tables()
	drop_timeline()
	drop_snapshots()
	drop_queries()
	print "--- All tables,queries and snapshots dropped"
	drop_function()
	print "---Auditing functions dropped"
	create_snapshot_sequence()
	reset_ids('id')
	# reset_ids('timeline_id_seq')
	reset_ids('snap_id')
	create_table()
	create_timeline()
	print "--- The normal and audit temporal log table created"
	db_function()
	print "--- Auditing mechanism turned on"
	print "--- The system is ready!"
	fcn.delete_firebase('activity')
	fcn.delete_firebase('chain_check')
	fcn.delete_firebase('components')
	fcn.delete_firebase('queries')	
	fcn.delete_firebase('record_signature')	
	fcn.delete_firebase('snapshotQuery')	
	fcn.delete_firebase('snapshots')	
	fcn.delete_firebase('trustworthiness')
	if os.path.exists("static/charts/elbow.png"):
		os.remove("static/charts/elbow.png")
	else:
		print("The file does not exist")


