from google.cloud import bigquery
import logging
import os


def insert_into_bigquery(client, record, project_id, dataset_id, table_id):
    try:
        table_ref = f"{project_id}.{dataset_id}.{table_id}"
        errors = client.insert_rows_json(table_ref, [record])
        if errors:
            logging.error(f"Errores al insertar en BigQuery: {errors}")
        else:
            logging.info("Inserción exitosa en BigQuery.")
    except Exception as e:
        logging.error(f"Error al ejecutar la función de BigQuery: {e}")

