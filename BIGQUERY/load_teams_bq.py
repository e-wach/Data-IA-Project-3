#!/usr/bin/env python3
import os
import json
import logging

from google.cloud import pubsub_v1
from google.cloud import bigquery

# 1) Configuración (puedes sobreescribir con variables de entorno)
PROJECT_ID        = os.getenv("GCP_PROJECT_ID", "western-mix-459018-g4")
SUBSCRIPTION_NAME = os.getenv("SUB_NBA_TEAMS", "nba_teams-sub")
DATASET_ID        = os.getenv("BQ_DATASET", "nba_dataset")
TABLE_ID          = os.getenv("BQ_TABLE", "teams")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    """
    Procesa cada mensaje:
      - Decodifica JSON
      - Lo inserta en BigQuery
      - Hace ACK si todo va bien, NACK en caso contrario
    """
    try:
        payload = json.loads(message.data.decode("utf-8"))
        logging.info(f"Recibido mensaje: {payload}")

        # Inserción en BigQuery
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
    """Inicia el listener de Pub/Sub y mantiene el proceso vivo."""
    subscriber = pubsub_v1.SubscriberClient()
    sub_path   = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

    streaming_pull = subscriber.subscribe(sub_path, callback=callback)
    logging.info(f"Escuchando mensajes en {sub_path}...")

    # Ctrl+C para detener
    try:
        streaming_pull.result()
    except KeyboardInterrupt:
        streaming_pull.cancel()
        logging.info("Listener detenido.")

if __name__ == "__main__":
    main()
