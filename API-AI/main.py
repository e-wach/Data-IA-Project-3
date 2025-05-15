from flask import Flask, jsonify
import psycopg2
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "data-ia-project-3")
SQL_HOST = os.getenv("SQL_HOST", "DEFAULT_HOST") #### PARA PROBAR EN LOCAL, PONER LA IP PÚBLICA DE LA SQL INSTANCE
SQL_USER = os.getenv("SQL_USER", "nba_user")
SQL_PASS = os.getenv("SQL_PASS", "dataproject3")
SQL_DB = os.getenv("SQL_DB", "nba_database")

def get_postgres_connection():
    conn = psycopg2.connect(
        dbname=SQL_DB,
        user=SQL_USER,
        password=SQL_PASS,
        host=SQL_HOST,
        port="5432"
    )
    return conn


@app.route("/AgentSQL", methods=["GET"])
def get_sql_data():
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM injured_players")
        injured_data = cursor.fetchall()
        cursor.execute("SELECT * FROM nba_games_week")
        upcoming_data = cursor.fetchall()
        cursor.execute("SELECT * FROM game_odds")
        odds_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({
            "injured_players": injured_data,
            "nba_games_week": upcoming_data,
            "game_odds": odds_data
        })
    except Exception as e:
        logging.error(f"Error fetching SQL data: {str(e)}")
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8081)


