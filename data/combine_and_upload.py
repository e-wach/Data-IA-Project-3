import os
import glob
import json
from google.cloud import storage


PROJECT_ID  = "western-mix-459018-g4"
BUCKET_NAME = "bucket-nba"


DATA_DIR      = os.path.join(os.path.dirname(__file__), "..", "data")
NDJSON_DIR    = os.path.join(os.path.dirname(__file__), "ndjson")
OUTPUT_FILE   = os.path.join(NDJSON_DIR, "all_games.ndjson")


GCS_OBJECT_NAME = "all_games.ndjson"



def combine_json_to_ndjson():
    """Convierte todos los JSON-array de DATA_DIR en un único NDJSON."""
    os.makedirs(NDJSON_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as dst:
        for path in glob.glob(os.path.join(DATA_DIR, "*.json")):
            print(f"→ Procesando {os.path.basename(path)}")
            with open(path, "r") as src:
                for record in json.load(src):
                    dst.write(json.dumps(record) + "\n")
    print(f"✔ NDJSON combinado en {OUTPUT_FILE}")

def upload_ndjson_to_gcs():
    """Sube OUTPUT_FILE al bucket BUCKET_NAME."""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(GCS_OBJECT_NAME)
    blob.upload_from_filename(OUTPUT_FILE)
    uri = f"gs://{BUCKET_NAME}/{GCS_OBJECT_NAME}"
    print(f"↑ Subido a {uri}")
    return uri

def main():
    combine_json_to_ndjson()
    upload_ndjson_to_gcs()
    print("¡Listo! Cuando este archivo llegue al bucket, la Cloud Function se encargará de insertar en BigQuery.")

if __name__ == "__main__":
    main()
