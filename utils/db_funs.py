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