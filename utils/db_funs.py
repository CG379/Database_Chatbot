import psycopg2
# TODO: Import creds

# get db connection 
try:
    # TODO: Add creds
    db_connection = psycopg2.connect()
    db_connection.set_session(autocommit=True)
except Exception as e:
    print(f"Unable to connect to the database: {e}")

# allows for interaction with the db, all changes are immediately visible
curser = db_connection.cursor()

# TODO: Validate connection



def get_schema_names(db_connection):
    curser = db_connection.cursor()
