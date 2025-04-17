import psycopg2
from utils.config import db_credentials

# Global variable to store database connection
db_connection = None

def get_db_connection():
    """Get or create a database connection"""
    global db_connection
    if db_connection is None or db_connection.closed:
        try:
            db_connection = psycopg2.connect(
                host=db_credentials['host'],
                user=db_credentials['user'],
                password=db_credentials['password'],
                port=db_credentials['port'],
                database=db_credentials['default_db']
            )
            db_connection.set_session(autocommit=True)
            return db_connection
        except Exception as e:
            print(f"Unable to connect to the database: {e}")
            return None
    return db_connection

# Initialize connection
db_connection = get_db_connection()

# allows for interaction with the db, all changes are immediately visible
curser = db_connection.cursor()

# TODO: Validate connection
if db_connection.closed == 0:
    print("Connected to the database")
else:
    print("Failed to connect to the database")

# Get Schema Names
def get_schema_names(db_connection):
    if not db_connection:
        return []
    try:
        curser = db_connection.cursor()
        curser.execute("SELECT schema_name FROM information_schema.schemata;")
        schema_names = [row[0] for row in curser.fetchall()]
        return schema_names
    except Exception as e:
        print(f"Error getting schema names: {e}")
        return []

# Get Table Names
def get_table_names(db_connection, schema_name):
    if not db_connection:
        return []
    try:
        curser = db_connection.cursor()
        curser.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}';")
        table_names = [row[0] for row in curser.fetchall()]
        return table_names
    except Exception as e:
        print(f"Error getting table names: {e}")
        return []

# Get column names
def get_column_names(db_connection, table_name, schema_name):
    if not db_connection:
        return []
    try:
        curser = db_connection.cursor()
        curser.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}' AND table_schema = '{schema_name}';")
        column_names = [row[0] for row in curser.fetchall()]
        return column_names
    except Exception as e:
        print(f"Error getting column names: {e}")
        return []

# Get db info
def get_db_info(db_connection, schema_names):
    if not db_connection:
        return []
    table_dicts = []
    try:
        for schema_name in schema_names:
            for table_name in get_table_names(db_connection, schema_name):
                table_dict = {
                    'schema_name': schema_name,
                    'table_name': table_name,
                    'column_names': get_column_names(db_connection, table_name, schema_name)
                }
                table_dicts.append(table_dict)
    except Exception as e:
        print(f"Error getting database info: {e}")
    return table_dicts

# Initialize schema data
schemas = ['public']
db_schema_dict = get_db_info(db_connection, schemas)
database_schema_string = "\n".join(
    [
        f"Schema: {table['schema_name']}\nTable: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
        for table in db_schema_dict
    ]
) if db_schema_dict else "No database connection available"

def execute_query(db_connection, query):
    if not db_connection:
        return "No database connection available"
    try:
        curser = db_connection.cursor()
        curser.execute(query)
        result = str(curser.fetchall())
        curser.close()
        return result
    except Exception as e:
        return f'Query Failed: {e}'

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


def import_csv_to_table(db_connection, table_name, df, schema='public'):
    """Import a pandas DataFrame into a new table in the database"""
    if not db_connection:
        return "No database connection available"
    
    try:
        cursor = db_connection.cursor()
        
        # Create table with appropriate column types
        columns = []
        for col, dtype in df.dtypes.items():
            if dtype == 'object':
                col_type = 'TEXT'
            elif dtype == 'int64':
                col_type = 'BIGINT'
            elif dtype == 'float64':
                col_type = 'DOUBLE PRECISION'
            elif dtype == 'datetime64[ns]':
                col_type = 'TIMESTAMP'
            else:
                col_type = 'TEXT'
            columns.append(f'"{col}" {col_type}')
        
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table_name} (
            {', '.join(columns)}
        )
        """
        cursor.execute(create_table_query)
        
        # Insert data
        for _, row in df.iterrows():
            placeholders = ', '.join(['%s'] * len(row))
            columns_str = ', '.join([f'"{col}"' for col in df.columns])
            insert_query = f"""
            INSERT INTO {schema}.{table_name} ({columns_str})
            VALUES ({placeholders})
            """
            cursor.execute(insert_query, tuple(row))
        
        db_connection.commit()
        return f"Successfully imported data into {schema}.{table_name}"
        
    except Exception as e:
        db_connection.rollback()
        return f"Error importing data: {str(e)}"
    finally:
        cursor.close()

# To print details to the console:
# schemas = get_schema_names(postgres_connection)
# here you need to set schema name from postgres by default the schema is public in postgres database. you can see in pgadmin
schemas = ['public']
db_schema_dict = get_db_info(db_connection, schemas)
database_schema_string = "\n".join(
    [
        f"Schema: {table['schema_name']}\nTable: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
        for table in db_schema_dict
    ]
)