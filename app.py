from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from ai_helper import embed_note_and_store, rag_query # type: ignore

app = Flask(__name__)
DB_NAME = "notes.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
init_db()

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        notes = conn.execute("SELECT * FROM notes").fetchall()
    return render_template('index.html', notes=notes)

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        note_id = cur.lastrowid
    embed_note_and_store(note_id, title, content)  # <--- Add this line
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
def ask():
    query = request.form['query']
    results = rag_query(query)  # Use new function
    with sqlite3.connect(DB_NAME) as conn:
        notes = conn.execute("SELECT * FROM notes").fetchall()
    return render_template('index.html', notes=notes, results=results)



if __name__ == '__main__':
    app.run(debug=True)
