from google.cloud import bigquery
import mysql.connector

client = bigquery.Client()

SQL_HOST =""
SQL_USER = ""
SQL_PASS = ""
SQL_DB = ""
SQL_DIR = ""
INSTANCE_ID = ""

def connect_to_db(PROJECT_ID, REGION):
    connection = mysql.connector.connect(
        user=SQL_USER,
        password=SQL_PASS,
        database=SQL_DB,
        unix_socket=f"{SQL_DIR}/{PROJECT_ID}:{REGION}:{INSTANCE_ID}"
    )
    return connection


def query_bigquery(PROJECT_ID, REGION):
    query = """
    <QUERY AGENT AI>
    """
    query_job = client.query(query)
    results = query_job.result()
    db_connection = connect_to_db(PROJECT_ID, REGION)
    cursor = db_connection.cursor()
    for row in results:
        K = row["v"]
        insert_query = """
       INSERT INTO ... 
        """
        cursor.execute(insert_query, (K,))
    db_connection.commit()
    cursor.close()
    db_connection.close()
    return "Datos insertados correctamente a SQL"

