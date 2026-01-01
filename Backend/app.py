from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import pickle
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from string import punctuation

app = Flask(__name__)
CORS(app)

# 1. Load the "Brain" and the "Dictionary"
model = tf.keras.models.load_model('spam_model.h5')
with open('tokenizer.pkl', 'rb') as handle:
    tokenizer = pickle.load(handle)

# 2. Setup NLP tools (must match train_model.py exactly)
stop_words = set(stopwords.words("english"))
lem = WordNetLemmatizer()

def clean_input(text):
    text = text.lower()
    tokens = word_tokenize(text)
    # Remove stopwords, punctuation, and lemmatize
    clean_tokens = [lem.lemmatize(t) for t in tokens if t not in stop_words and t not in punctuation]
    return " ".join(clean_tokens)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    raw_text = data.get("text", "")
    
    if not raw_text:
        return jsonify({"error": "No text provided"}), 400

    # --- Step A: Clean the user's text ---
    cleaned_text = clean_input(raw_text)

    # --- Step B: Convert text to numbers (Tokenization) ---
    # The tokenizer remembers the word numbers from your training data
    seq = tokenizer.texts_to_sequences([cleaned_text])
    padded = pad_sequences(seq, maxlen=100, padding='post', truncating='post')

    # --- Step C: Predict using the AI ---
    prediction = model.predict(padded)[0][0] # Returns a number between 0 and 1
    
    # Logic: Closer to 1 is Spam, Closer to 0 is Ham
    label = "Spam/Negative" if prediction > 0.5 else "Ham/Positive"
    confidence = float(prediction if prediction > 0.5 else 1 - prediction)

    # --- Step D: Extract Keywords for UI ---
    # Show the user which words the AI found important
    words_found = [w for w in cleaned_text.split() if w in tokenizer.word_index][:6]

    return jsonify({
        "label": label,
        "score": confidence,
        "keywords": words_found
    })

if __name__ == '__main__':
    print("Server starting... Model is live!")
    app.run(debug=True, port=5000)