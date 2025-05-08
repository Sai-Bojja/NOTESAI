from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from ai_helper import embed_note_and_store, rag_query, clear_chroma_notes # type: ignore

#from ai_helper import clear_chroma_notes  # or reset_chroma_notes


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
        notes = conn.execute("SELECT id, title FROM notes").fetchall()
    return render_template('index.html', notes=notes, results=None)

@app.route('/add', methods=['POST'])
def add_note():
    title = request.form['title']
    content = request.form['content']
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        note_id = cur.lastrowid
    embed_note_and_store(note_id, title, content)  
    return redirect(url_for('index'))

@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
def ask():
    query = request.form['query']
    results = rag_query(query)  
    with sqlite3.connect(DB_NAME) as conn:
        notes = conn.execute("SELECT id, title FROM notes").fetchall()
    return render_template('index.html', notes=notes, results=results)

@app.route("/clear_notes", methods=["POST"])
def clear_notes():
    clear_chroma_notes()  # or reset_chroma_notes()
    return jsonify({"message": "All notes cleared successfully!"}) # type: ignore

@app.route('/get_note/<int:note_id>')
def get_note(note_id):
    with sqlite3.connect(DB_NAME) as conn:
        note = conn.execute("SELECT title, content FROM notes WHERE id = ?", (note_id,)).fetchone()
        if note:
            return jsonify({'id': note_id, 'title': note[0], 'content': note[1]})
        else:
            return jsonify({'error': 'Note not found'}), 404



if __name__ == '__main__':
    app.run(debug=True)
