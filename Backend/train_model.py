import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import nltk

from nltk.corpus import stopwords
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
from wordcloud import WordCloud

import tensorflow as tf

from string import punctuation
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split


from keras.callbacks import EarlyStopping, ReduceLROnPlateau

import warnings
warnings.filterwarnings('ignore')

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

data=pd.read_csv('spam_ham_dataset.csv')

# splitting data-- You are separating your big dataset into two smaller piles: one containing only normal emails (ham_msg) and one containing only spam emails (spam_msg).


ham_msg=data[data['label']=='ham']
spam_msg=data[data['label']=='spam']

ham_msg_balanced=ham_msg.sample(n=len(spam_msg),random_state=42)
#  If you have 4000 Ham and 500 Spam, this line throws away 3500 Ham emails and keeps only 500 random ones. Now you have 500 Ham and 500 Spam.
# random_state=42: This ensures that every time you run the code, you pick the same random emails (good for consistent results).
# reset_index: This cleans up the row numbers (0, 1, 2...) so they are in order again.
balanced_data=pd.concat([ham_msg_balanced,spam_msg],axis=0).reset_index(drop=True)

lem=WordNetLemmatizer()
stopwords=set(stopwords.words("english"))

def clean_function(text):
    text=text.lower()
    text=word_tokenize(text)
    text=[t for t in text if t not in stopwords]
    text=[t for t in text if t not in punctuation]
    text=[lem.lemmatize(t) for t in text]
    text=" ".join(text)
    return text

balanced_data['clean_text']=balanced_data['text'].apply(clean_function)

clean_text=" ".join(balanced_data['clean_text'])

# wc=WordCloud(
#     background_color="white",
#     width=600,height=400,
#     colormap="plasma",max_words=100
# ).generate(clean_text)
# plt.figure(figsize=(10,6))
# plt.imshow(wc,interpolation='bilinear')
# plt.axis('off')
# plt.show()

# --- STEP 1: PREPARE DATA ---
# Use the text strings directly for the split
X = balanced_data['clean_text'].astype(str).values
y = (balanced_data['label'] == 'spam').astype(int).values

train_X, test_X, train_Y, test_Y = train_test_split(X, y, test_size=0.2, random_state=42)

# --- STEP 2: TOKENIZATION (The Keras Way) ---
tokenizer = Tokenizer()
tokenizer.fit_on_texts(train_X) # <--- MUST fit on text strings

# Convert strings to sequences of integers
train_seq = tokenizer.texts_to_sequences(train_X)
test_seq = tokenizer.texts_to_sequences(test_X)

# --- STEP 3: PADDING ---
max_len = 100
train_sequences = pad_sequences(train_seq, maxlen=max_len, padding='post', truncating='post')
test_sequences = pad_sequences(test_seq, maxlen=max_len, padding='post', truncating='post')

# --- STEP 4: MODEL BUILDING ---
vocab_size = len(tokenizer.word_index) + 1

model = tf.keras.models.Sequential([
    # vocab_size tells the AI how many unique words it needs to know
    tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=32, input_length=max_len),
    tf.keras.layers.LSTM(16),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid') 
])

model.compile(
    loss='binary_crossentropy', # Use string name for standard sigmoid output
    optimizer='adam',
    metrics=['accuracy']
)

model.summary()

# --- STEP 5: TRAINING ---
print("Starting Training...")
history = model.fit(
    train_sequences, train_Y,
    epochs=10,
    validation_data=(test_sequences, test_Y),
    callbacks=[EarlyStopping(monitor='val_loss', patience=3)]
)

import pickle

# Save the model
model.save('spam_model.h5')

# Save the tokenizer
with open('tokenizer.pkl', 'wb') as handle:
    pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)

print("Model and Tokenizer saved successfully!")