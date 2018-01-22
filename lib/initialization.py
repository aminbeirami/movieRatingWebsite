def db_function(): #turns on the triggers. if there are no triggers, it generates the triggers.
	sql = '''
		CREATE FUNCTION log_data()
		RETURNS TRIGGER
		LANGUAGE PLPGSQL
		AS
		$$
		  BEGIN
		    IF (TG_OP = 'DELETE') THEN
		        INSERT INTO timeline (r_id, username, movie_name, rating, lat, long, ttime, deleted)
		        SELECT OLD.id, NULL, NULL, NULL, NULL, NULL, NULL, TRUE;
		        RETURN OLD;
		    ELSIF (TG_OP = 'UPDATE') THEN
		        INSERT INTO timeline (r_id,username, movie_name, rating, lat, long, ttime, deleted)
		        SELECT NEW.id, NEW.usr_id, NEW.mv_name, NEW.rating,NEW.lat,NEW.long,NOW(),FALSE;
		        RETURN NEW;
		    ELSIF (TG_OP = 'INSERT') THEN
		        INSERT INTO timeline (r_id, username, movie_name, rating, lat, long, ttime, deleted)
		        SELECT NEW.id, NEW.usr_id, NEW.mv_name, NEW.rating,NEW.lat,NEW.long,NOW(),FALSE;
		        RETURN NEW;
		    END IF;
		    RETURN NULL;
		  END;
		$$;
		'''
	db.command(sql)
	db.commit()

	sql = '''CREATE TRIGGER base_data_log
		AFTER INSERT OR UPDATE OR DELETE ON rating
		FOR EACH ROW EXECUTE PROCEDURE log_data()
		'''
	db.command(sql)
	db.commit()
	print 'relevant triggers created'

def create_Database(): 
  cur.execute("CREATE TABLE IF NOT EXISTS rating (id SERIAL,usr_id INT,mv_name TEXT,rating INT, lat TEXT,long TEXT)")
  conn.commit()
  print 'relevant databases created successfully!'
