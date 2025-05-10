#!/usr/bin/env python3
import os
import json
import logging

from google.api_core.exceptions import NotFound
from google.cloud import pubsub_v1
from google.cloud import bigquery

# 1) Configuración
PROJECT_ID        = os.getenv("GCP_PROJECT_ID", "western-mix-459018-g4") # Cambiar por tu proyecto
SUBSCRIPTION_NAME = os.getenv("SUB_NBA_ODDS", "nba_odds-sub")
DATASET_ID        = os.getenv("BQ_DATASET",    "nba_dataset")
TABLE_ID          = os.getenv("BQ_TABLE",      "nba_odds")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# 2) Esquema embebido para BigQuery
SCHEMA = [
    bigquery.SchemaField("game_id",        "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("home_team_id",   "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("away_team_id",   "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("market_name",    "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("odds_type_id",   "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("group_name",     "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("book_name",      "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("country_code",   "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("book_url",       "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("odds_type",      "STRING",  mode="REQUIRED"),
    bigquery.SchemaField("odds",           "FLOAT",   mode="NULLABLE"),
    bigquery.SchemaField("opening_odds",   "FLOAT",   mode="NULLABLE"),
    bigquery.SchemaField("odds_trend",     "FLOAT",   mode="NULLABLE"),
]

def ensure_bq_table():
    """Crea dataset y tabla si no existen."""
    bq = bigquery.Client(project=PROJECT_ID)
    ds_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    tbl_ref = ds_ref.table(TABLE_ID)

    # Dataset
    try:
        bq.get_dataset(ds_ref)
        logging.info(f"Dataset {DATASET_ID} ya existe.")
    except NotFound:
        ds = bigquery.Dataset(ds_ref)
        ds.location = "EU"  # ajústalo si usas otra región
        bq.create_dataset(ds)
        logging.info(f"Dataset {DATASET_ID} creado.")

    # Tabla
    try:
        bq.get_table(tbl_ref)
        logging.info(f"Tabla {TABLE_ID} ya existe.")
    except NotFound:
        table = bigquery.Table(tbl_ref, schema=SCHEMA)
        bq.create_table(table)
        logging.info(f"Tabla {TABLE_ID} creada con esquema.")

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    """Procesa cada mensaje Pub/Sub e inserta en BigQuery."""
    try:
        payload = json.loads(message.data.decode("utf-8"))
        logging.debug(f"Recibido mensaje: {payload}")

        bq = bigquery.Client(project=PROJECT_ID)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        errors = bq.insert_rows_json(table_ref, [payload])

        if errors:
            logging.error(f"Errores al insertar en BQ: {errors}")
            message.nack()
        else:
            logging.info("Insertado correctamente en BigQuery.")
            message.ack()

    except Exception as e:
        logging.exception(f"Excepción procesando mensaje: {e}")
        message.nack()

def main():
    ensure_bq_table()
    subscriber = pubsub_v1.SubscriberClient()
    sub_path   = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

    streaming_pull = subscriber.subscribe(sub_path, callback=callback)
    logging.info(f"Escuchando mensajes en {sub_path}...")

    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        streaming_pull.cancel()
        logging.info("Listener detenido.")

if __name__ == "__main__":
    main()
