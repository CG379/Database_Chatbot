import psycopg2
from utils.config import db_credentials

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
if db_connection.closed == 0:
    print("Connected to the database")
else:
    print("Failed to connect to the database")

# Get Schema Names
def get_schema_names(db_connection):
    curser = db_connection.cursor()
    curser.execute("SELECT schema_name FROM information_schema.schemata;")
    schema_names = [row[0] for row in curser.fetchall()]
    return schema_names

# Get Table Names
def get_table_names(db_connection, schema_name):
    curser = db_connection.cursor()
    curser.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';")
    table_names = [row[0] for row in curser.fetchall()]
    return table_names

# Get coloumn names
def get_column_names(db_connection, table_name, schema_name):
    curser = db_connection.cursor()
    curser.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = '{schema_name}';")
    column_names = [row[0] for row in curser.fetchall()]
    return column_names

# Get db info
def get_db_info(db_connection, schema_names):
    table_dicts = []

    for schema_name in schema_names:
        for table_name in get_table_names(db_connection, schema_name):
            table_dict = {
                'schema_name': schema_name,
                'table_name': table_name,
                'column_names': get_column_names(db_connection, table_name, schema_name)
            }
            table_dicts.append(table_dict)
    return table_dicts

schemas = ['prod', 'dev', 'test']
bd_schema_dict = get_db_info(db_connection, schemas)
print(bd_schema_dict)
db_schema_string = "\\n".join([
    f"Schema: {table['schema_name']}\\nTable: {table['table_name']}\\nColumns: {', '.join(table['column_names'])}" for table in bd_schema_dict
    ])

def execute_query(db_connection, query):
    try:
        curser = db_connection.cursor()
        curser.execute(query)
        result = str(curser.fetchall())
        curser.close()
    except Exception as e:
        result = f'Query Failed: {e}'
    return result

# TODO: get api data
def get_api_data():
    pass


def create_db(name):
    """Create a new PostgreSQL database and set up initial tables"""
    try:
        # Connect to default database first
        init_connection = psycopg2.connect(
            host=db_credentials['host'],
            user=db_credentials['user'],
            password=db_credentials['password'],
            database="postgres"  # Connect to default db to create new one
        )
        init_connection.set_session(autocommit=True)
        cursor = init_connection.cursor()

        # Create new database
        cursor.execute(f"CREATE DATABASE {name}")
        
        cursor.close()
        init_connection.close()

        # Connect to the newly created database
        # TODO: Grab name of db
        db_credentials['dbname'] = name
        conn = psycopg2.connect(**db_credentials)
        conn.set_session(autocommit=True)
        cur = conn.cursor()

        # Create schemas
        for schema in ['prod', 'dev', 'test']:
            cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

        # Example table creation in prod schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        """)

        conn.commit()
        print("Table created successfully!")
        
        # Example data import function
        def import_data_from_api(table_name, data):
            """Import data into specified table"""
            if not data:
                return "No data to import"
            
            columns = data[0].keys()
            values = [tuple(row.values()) for row in data]
            
            columns_str = ', '.join(columns)
            values_template = ', '.join(['%s'] * len(columns))
            
            query = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({values_template})
            """
            
            cur.executemany(query, values)
            return f"Data imported successfully into {table_name}"

        cur.close()
        conn.close()
        
        return "Database created successfully!"

    except psycopg2.Error as e:
        return f"Failed to create database: {str(e)}"


def drop_database():
    """Drop the entire database - USE WITH CAUTION"""
    try:
        # Connect to default database
        init_connection = psycopg2.connect(
            host=db_credentials['host'],
            user=db_credentials['user'],
            password=db_credentials['password'],
            database="postgres"  # Connect to different database to drop current one
        )
        init_connection.set_session(autocommit=True)
        cursor = init_connection.cursor()

        # Force disconnect all other clients
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_credentials['dbname']}'
            AND pid <> pg_backend_pid();
        """)
        
        # Drop database
        cursor.execute(f"DROP DATABASE IF EXISTS {db_credentials['dbname']}")
        
        cursor.close()
        init_connection.close()
        
        return "Database dropped successfully!"

    except psycopg2.Error as e:
        return f"Failed to drop database: {str(e)}"