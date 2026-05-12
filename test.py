import torch
import tensorflow as tf
import pickle
import numpy as np
from src.model import SentimentANN

# --- 1. AYARLAR (Eğitimdekiyle BİREBİR AYNI OLMALI) ---
VOCAB_SIZE = 30000
MAX_LEN = 100
EMBED_DIM = 128
HIDDEN_DIM = 64

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- 2. MODEL VE TOKENIZER'I YÜKLE ---
# Tokenizer'ı yükle
with open('models/tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

# Modeli oluştur ve ağırlıkları yükle
model = SentimentANN(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM).to(device)
model.load_state_dict(torch.load('models/sentiment_model.pth', map_location=device))
model.eval() # Test modu

print(f"Model ve Tokenizer başarıyla yüklendi. Cihaz: {device}")

# --- 3. TAHMİN FONKSİYONU ---
def predict_sentiment(text):
    # Metni temizleme (İsteğe bağlı, eğitimdeki gibi yapılabilir)
    text = text.lower()
    
    # Sayısal diziye çevir
    sequence = tokenizer.texts_to_sequences([text])
    
    # Padding yap (Eğitimdeki uzunlukta)
    padded = tf.keras.preprocessing.sequence.pad_sequences(
        sequence, maxlen=MAX_LEN, padding='post', truncating='post'
    )
    
    # PyTorch Tensor'e çevir
    input_tensor = torch.tensor(padded, dtype=torch.long).to(device)
    
    # Tahmin yap
    with torch.no_grad():
        output = model(input_tensor)
        score = output.item()
    
    # Sonucu yorumla
    status = "POZİTİF" if score > 0.5 else "NEGATİF"
    return status, score

# --- 4. TEST ALANI ---
if __name__ == "__main__":
    while True:
        user_input = input("\nYorumunuzu yazın (Çıkmak için 'q' tuşuna basın): ")
        if user_input.lower() == 'q':
            break
            
        label, confidence = predict_sentiment(user_input)
        print(f"Sonuç: {label} | Skor: {confidence:.4f}")