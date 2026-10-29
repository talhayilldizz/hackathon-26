import torch
from services.json_tokenizer import JsonTokenizer
from src.model import SentimentANN

# Sabit Ayarlar
VOCAB_SIZE = 30000
MAX_LEN = 100
EMBED_DIM = 128
HIDDEN_DIM = 64

class ModelService:
    def __init__(self, model_path='models/sentiment_model.pth', tokenizer_path='models/tokenizer.json'):
        # M4 Mac için en hızlısı: mps
        self.device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
        
        try:
            self.tokenizer = JsonTokenizer(tokenizer_path)

            self.model = SentimentANN(VOCAB_SIZE, EMBED_DIM, HIDDEN_DIM).to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device, weights_only=True))
            self.model.eval()
            print(f"✅ CartWise AI Servisi Aktif! Cihaz: {self.device}")
        except Exception as e:
            print(f"❌ Başlatma Hatası: {e}")

    def tekli_tahmin(self, metin):
        metin = metin.lower()
        
        # Tokenize işlemi
        sequence = self.tokenizer.texts_to_sequences([metin])[0]
        
        # --- TENSORFLOW YERİNE SAF PYTHON PADDING ---
        if len(sequence) > MAX_LEN:
            padded_seq = sequence[:MAX_LEN]
        else:
            padded_seq = sequence + [0] * (MAX_LEN - len(sequence))
        # --------------------------------------------

        # PyTorch Tensor'e çevirip cihaza yolla
        input_tensor = torch.tensor([padded_seq], dtype=torch.long).to(self.device)

        with torch.no_grad():
            output = self.model(input_tensor)
            return output.item()
        
    def toplu_analiz(self, yorumlar):
        # Yorumlar listede değilse veya boşsa güvenli çıkış yapalım
        if not yorumlar:
            return {"durum": "Veri Yok", "oran": 0}

        pozitif_sayisi = 0
        toplam_yorum = len(yorumlar)

        for y in yorumlar:
            # y bir sözlükse (metin anahtarıyla), değilse direkt string kabul et
            metin = y['metin'] if isinstance(y, dict) else y
            skor = self.tekli_tahmin(metin)
            if skor > 0.5:
                pozitif_sayisi += 1
        
        pozitif_orani = (pozitif_sayisi / toplam_yorum) * 100
        
        # Jürinin gözüne hitap edecek durum metinleri
        if pozitif_orani > 65:
            durum = "YÜKSEK FIRSAT"
        elif pozitif_orani > 40:
            durum = "RİSKLİ / BELİRSİZ"
        else:
            durum = "UZAK DURUN"
            
        return {
            "durum": durum,
            "oran" : round(pozitif_orani, 2)
        }