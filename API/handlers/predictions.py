from google.cloud import bigquery
import psycopg2

client = bigquery.Client()

SQL_PORT = "5432"  

def connect_to_db(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB):
    connection = psycopg2.connect(
        host=SQL_HOST,
        user=SQL_USER,
        password=SQL_PASS,
        dbname=SQL_DB,
        port=SQL_PORT
    )
    return connection

def query_bigquery(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB):
    query = """
    <QUERY AGENT AI>
    """
    query_job = client.query(query)
    results = query_job.result()
    db_connection = connect_to_db()
    cursor = db_connection.cursor(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
    for row in results:
        K = row["v"]
        insert_query = """
        INSERT INTO ... 
        """
        cursor.execute(insert_query, (K,))
    db_connection.commit()
    cursor.close()
    db_connection.close()
    return "Agent predictions inserted successfully into PostgreSQL"