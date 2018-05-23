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
		        INSERT INTO timeline (id,rec_id, mov_id, mv_name, mv_year,release_date,movie_url,star,user_id,username,signature,__flag__,__t__)
		        SELECT NEXTVAL('id'), OLD.id, NULL, NULL, NULL, NULL, NULL, NULL, NULL,NULL,NULL,1,NOW();
		        RETURN OLD;
		    ELSIF (TG_OP = 'UPDATE') THEN
		        INSERT INTO timeline 
		        SELECT NEXTVAL('id'), NEW.id , NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,0,NOW();
		        RETURN NEW;
		    ELSIF (TG_OP = 'INSERT') THEN
		        INSERT INTO timeline
		        SELECT NEXTVAL('id'), NEW.id , NEW.mov_id, NEW.mv_name, NEW.mv_year,NEW.release_date,NEW.movie_url,NEW.star,NEW.user_id,NEW.username,NEW.signature,0,NOW();
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
	print 'relevant triggers created'

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
  	print 'relevant databases created successfully!'
# (rec_id, mov_id, mv_name, mv_year,release_date,movie_url,star,user_id,username,signature,__flag__,__t__)