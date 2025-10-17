from flask import Flask
import psycopg2
import os
from dotenv import load_dotenv
from flask_cors import  CORS
load_dotenv()
app = Flask(__name__)
CORS(app)
conn = psycopg2.connect(
    host=os.getenv("PGHOST"),
    user=os.getenv("PGUSER"),
    password=os.getenv("PGPASSWORD"),
    database=os.getenv("PGDATABASE")
)
cursor = conn.cursor()

@app.route("/")
def hello():
    if cursor:
        return "db connected"
    return "de connection failed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
