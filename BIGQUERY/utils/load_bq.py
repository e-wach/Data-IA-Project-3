from google.cloud import bigquery
import logging
import os


def insert_into_bigquery(client, record, project_id, dataset_id, table_id):
    try:
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, [record])
        if errors:
            logging.error(f"Error inserting into BigQuery: {errors}")
        else:
            logging.info("Data inserted intO BigQuery sucessfully.")
    except Exception as e:
        logging.error(f"Error running BigQuery function: {e}")

