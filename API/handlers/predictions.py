from google.cloud import bigquery
import psycopg2
import logging

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

def get_predictions(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB):
    try:
        query = """
        SELECT * FROM ML.FORECAST(MODEL `data-ia-project-3.nba_dataset.modelo_prediccion_puntos`,
        STRUCT(1 AS horizon, 0.8 AS confidence_level)) 
        """
        query_job = client.query(query)
        results = query_job.result()
        db_connection = connect_to_db(SQL_HOST, SQL_USER, SQL_PASS, SQL_DB)
        cursor = db_connection.cursor()
        create_query = """
            CREATE TABLE IF NOT EXISTS predictions (
            team_id INT,
            forecast_timestamp TIMESTAMP WITH TIME ZONE,
            forecast_value FLOAT,
            standard_error FLOAT,
            confidence_level FLOAT,
            prediction_interval_lower_bound FLOAT,
            prediction_interval_upper_bound FLOAT,
            confidence_interval_lower_bound FLOAT,
            confidence_interval_upper_bound FLOAT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )"""
        cursor.execute(create_query)
        delete_query = """
            DELETE FROM predictions
            WHERE created_at < NOW() - INTERVAL '1 day';
            """
        cursor.execute(delete_query)
        for row in results:
            row_dict = dict(row)
            insert_query = """
            INSERT INTO predictions (
            team_id,
            forecast_timestamp,
            forecast_value,
            standard_error,
            confidence_level,
            prediction_interval_lower_bound,
            prediction_interval_upper_bound,
            confidence_interval_lower_bound,
            confidence_interval_upper_bound
        )
        VALUES (
            %(team_id)s,
            %(forecast_timestamp)s,
            %(forecast_value)s,
            %(standard_error)s,
            %(confidence_level)s,
            %(prediction_interval_lower_bound)s,
            %(prediction_interval_upper_bound)s,
            %(confidence_interval_lower_bound)s,
            %(confidence_interval_upper_bound)s
        );
            """
            cursor.execute(insert_query, row_dict)
        db_connection.commit()
        cursor.close()
        db_connection.close()
    except Exception as e:
        logging.error(f"Error inserting predictions into PostgresSQL: {e}")
