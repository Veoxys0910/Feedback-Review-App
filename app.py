import sqlite3

from flask import Flask, request, flash, redirect, url_for, render_template, g
import psycopg2
import os
from dotenv import load_dotenv
from flask_cors import  CORS
load_dotenv()
app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("SECRET_KEY", "test_secret_key")

def get_db_connection():
    # Return cached connection if exists
    if hasattr(g, "_database"):
        return g._database

    testing_mode = app.config.get("TESTING") or os.getenv("GITHUB_ACTIONS") == "true"

    if testing_mode:
        # Use SQLite in-memory DB for GitHub Actions or pytest
        conn = sqlite3.connect(":memory:", check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                message TEXT,
                is_read BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        g._database = conn
        app.logger.info("✅ Using SQLite for testing environment")
    else:
        # Use PostgreSQL in normal run
        conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            user=os.getenv("PGUSER"),
            password=os.getenv("PGPASSWORD"),
            database=os.getenv("PGDATABASE")
        )
        g._database = conn
        app.logger.info("✅ Connected to PostgreSQL database")

    return g._database

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form.get('name') or None
        message = request.form.get('message')

        if not message:
            flash('Message is required.')
            return redirect(url_for('index'))

        try:
            if isinstance(conn, sqlite3.Connection):
                cursor.execute("INSERT INTO feedback (name, message, is_read) VALUES (?, ?, 0)", (name, message))
            else:
                cursor.execute("INSERT INTO feedback (name, message, is_read) VALUES (%s, %s, false)", (name, message))
            conn.commit()
            return redirect(url_for('thank_you'))
        except Exception as e:
            conn.rollback()
            app.logger.error("Error inserting feedback: %s", e)
            flash('Failed to submit feedback.')
            return redirect(url_for('index'))

    return render_template('index.html')

@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/feedback')
def view_feedback():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, message, is_read FROM feedback ORDER BY id DESC")
    feedbacks = cursor.fetchall()
    return render_template('feedback.html', feedbacks=feedbacks)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


