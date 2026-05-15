import torch
import tensorflow as tf
import pickle
import numpy as np
from src.model import SentimentANN

VOCAB_SIZE = 30000
MAX_LEN = 100
EMBED_DIM = 128
HIDDEN_DIM = 64

class ModelService:
    def __init__(self, model_path='models/sentiment_model.pth', tokenizer_path='models/tokenizer.pickle'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        with open(tokenizer_path, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

        self.model = SentimentANN(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM).to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def tekli_tahmin(self, metin):
        metin = metin.lower()
        sequence = self.tokenizer.texts_to_sequences([metin])
        padded = tf.keras.preprocessing.sequence.pad_sequences(
            sequence, maxlen=MAX_LEN, padding='post', truncating='post'
        )

        input_tensor = torch.tensor(padded, dtype=torch.long).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            return output.item()
        
    def toplu_analiz(self, yorumlar):
        pozitif_sayisi = 0
        toplam_yorum = len(yorumlar)

        if toplam_yorum == 0:
            return "Yorum Yok", 0

        for y in yorumlar:
            skor = self.tekli_tahmin(y['metin'])
            if skor > 0.5:
                pozitif_sayisi += 1
        
        pozitif_orani = (pozitif_sayisi / toplam_yorum) * 100
        
        
        if pozitif_orani > 50:
            durum = "OLUMLU"
        else:
            durum = "OLUMSUZ"
            
        return {
            "durum": durum,
            "oran" : round(pozitif_orani, 2)
        }