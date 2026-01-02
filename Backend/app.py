import os
import sqlite3
import pickle
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from tensorflow.keras.preprocessing.sequence import pad_sequences
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Initialize Flask
app = Flask(__name__)
CORS(app)

# --- DATABASE SETUP ---
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    print("Initializing database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            label TEXT,
            score REAL,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    conn.close()
    print("Database ready.")

# Run initialization immediately
init_db()

# --- ML MODEL SETUP ---
print("Loading AI Model...")
model = tf.keras.models.load_model('spam_model.h5')
with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

stop_words = set(stopwords.words("english"))
lem = WordNetLemmatizer()

def clean_input(text):
    text = text.lower()
    tokens = word_tokenize(text)
    clean_tokens = [lem.lemmatize(t) for t in tokens if t not in stop_words]
    return " ".join(clean_tokens)

# --- ROUTES ---

@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        raw_text = data.get("text", "")
        
        # ML Prediction
        cleaned = clean_input(raw_text)
        seq = tokenizer.texts_to_sequences([cleaned])
        padded = pad_sequences(seq, maxlen=100, padding='post', truncating='post')
        prediction = model.predict(padded)[0][0]
        print(f"RAW AI OUTPUT: {prediction}") 
        
        label = "Spam" if prediction > 0.45 else "Ham"
        confidence = float(prediction if prediction > 0.5 else 1 - prediction)

        # SAVE TO DB
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO scans (text, label, score, timestamp) VALUES (?, ?, ?, ?)',
                       (raw_text[:100], label, confidence, datetime.now().isoformat()))
        conn.commit()
        conn.close()

        return jsonify({"label": label, "score": confidence})
    except Exception as e:
        print(f"Error in /api/analyze: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scans ORDER BY timestamp DESC LIMIT 50')
        rows = cursor.fetchall()
        history = [dict(row) for row in rows]
        conn.close()
        return jsonify(history)
    except Exception as e:
        print(f"Error in /api/history: {e}")
        return jsonify({"error": "Table not found. Perform a scan first."}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT label, COUNT(*) as count FROM scans GROUP BY label')
        rows = cursor.fetchall()
        conn.close()
        
        data = [{"name": row[0], "value": row[1]} for row in rows]
        return jsonify(data)
    except Exception as e:
        print(f"Error in /api/analytics: {e}")
        return jsonify([]), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)