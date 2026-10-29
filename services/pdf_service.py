from google import genai
from google.genai import types
import json
import re

class BankStatementAnalyzer:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview"

    def json_ayikla(self, metin):
        """Metin içindeki ilk { } bloğunu bulur ve temizler."""
        try:
            # Regex ile ilk { ve son } arasını yakalıyoruz
            match = re.search(r'(\{.*\})', metin, re.DOTALL)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            return None
        except Exception as e:
            print("PDF yanıtı ayrıştırılamadı.")
            return None

    def analiz_et(self, pdf_yolu):
        try:
            print("PDF gönderiliyor...")
            with open(pdf_yolu, "rb") as f:
                pdf_bytes = f.read()

            prompt = """
            Bu banka ekstresini analiz et. 
            Sadece şu JSON formatında yanıt ver:
            {"toplam_gelir": 0.0, "toplam_gider": 0.0, "ozet": "..."}
            """

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=pdf_bytes, mime_type='application/pdf')
                ]
            )


            sonuc = self.json_ayikla(response.text)
            if not sonuc:
                raise ValueError("AI geçerli bir JSON döndürmedi.")
                
            return sonuc

        except Exception as e:
            print("PDF analizi başarısız oldu.")
            return None
