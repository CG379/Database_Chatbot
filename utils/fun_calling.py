from utils.db_funs import database_schema_string

funs = [{
    "name": "execute_query",
    "description": "Use this function to answer questions about the database. Output should be an SQL query.",
    "params": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": f"""The SQL query that extracts information that answers the user's question from the Postgres database. 
                Write the SQL in the following schema structure: {database_schema_string}.
                Write the query in SQL fromat only. Do not include any line breaks or other characters that cannot be executed in Postgress.""",
            }
        },
        "required": ["query"],
    }

}]
