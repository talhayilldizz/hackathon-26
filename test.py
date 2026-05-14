import os
# DİKKAT: Bu satır her şeyden önce gelmeli! Keras'a PyTorch kullanmasını söylüyoruz.
os.environ["KERAS_BACKEND"] = "torch" 

import torch
import pickle
import numpy as np
from src.model import SentimentANN

# BURADAKİ import tensorflow as tf SATIRINI TAMAMEN SİLDİĞİNDEN EMİN OL!

# --- 1. AYARLAR ---
VOCAB_SIZE = 30000
MAX_LEN = 100
EMBED_DIM = 128
HIDDEN_DIM = 64

# M4 Mac için en hızlı cihaz seçimi (mps varsa mps, yoksa cpu)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

# --- 2. MODEL VE TOKENIZER'I YÜKLE ---
with open('models/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

model = SentimentANN(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM).to(device)
model.load_state_dict(torch.load('models/sentiment_model.pth', map_location=device))
model.eval()

print(f"✅ Sistem Hazır! Cihaz: {device}")

# --- 3. TAHMİN FONKSİYONU ---
def predict_sentiment(text):
    text = text.lower()
    
    # Kelimeleri sayılara çevir
    sequence = tokenizer.texts_to_sequences([text])
    
    # SAF PYTHON PADDING (TensorFlow gerektirmez)
    seq = sequence[0] if len(sequence) > 0 and len(sequence[0]) > 0 else []
    if len(seq) > MAX_LEN:
        padded_seq = seq[:MAX_LEN]
    else:
        padded_seq = seq + [0] * (MAX_LEN - len(seq))
    padded = [padded_seq]
    
    input_tensor = torch.tensor(padded, dtype=torch.long).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        score = output.item()
    
    status = "POZİTİF" if score > 0.5 else "NEGATİF"
    return status, score

if __name__ == "__main__":
    while True:
        user_input = input("\nYorumunuzu yazın (Çıkmak için 'q' tuşuna basın): ")
        if user_input.lower() == 'q':
            break
        label, confidence = predict_sentiment(user_input)
        print(f"Sonuç: {label} | Skor: {confidence:.4f}")