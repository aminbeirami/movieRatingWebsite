from lib import postgresCon as pc
from lib.config import *
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
		        INSERT INTO timeline (id,rec_id, mov_id, mv_name, mv_year,release_date,movie_url,star,user_id,username,signature,previous_signature,__flag__,__t__)
		        SELECT NEXTVAL('id'), OLD.id, NULL, NULL, NULL, NULL, NULL, NULL, NULL,NULL,NULL,(SELECT signature FROM timeline WHERE id = (SELECT last_value FROM id)),1,NOW();
		        RETURN OLD;
		    ELSIF (TG_OP = 'UPDATE') THEN
		        INSERT INTO timeline 
		        SELECT NEXTVAL('id'), NEW.id, NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,(SELECT signature FROM timeline WHERE id = (SELECT last_value FROM id)),0,NOW();
		        RETURN NEW;
		    ELSIF (TG_OP = 'INSERT') THEN
		        INSERT INTO timeline
		        SELECT NEXTVAL('id'), NEW.id , NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,(SELECT signature FROM timeline WHERE id = (SELECT last_value FROM id)),0,NOW();
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
	db.commit()
	print 'the sanp_id sequence was created.'

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

def init_everything():
	"--- started initialization..."
	drop_tables()
	drop_timeline()
	print "--- All tables dropped"
	drop_function()
	print "---Auditing functions dropped"
	create_snapshot_sequence()
	reset_ids('id')
	create_table()
	create_timeline()
	print "--- The normal and audit temporal log table created"
	db_function()
	print "--- Auditing mechanism turned on"
	print "--- The system is ready!"
