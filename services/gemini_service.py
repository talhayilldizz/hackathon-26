from google import genai
import json

class GeminiService:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview" 

    def finansal_danismanlik_yap(self, urun_verisi, analiz_sonucu, kisisel_baglam):
        """
        PyTorch modelinden gelen veriyi ve kullanıcı profilini birleştirip
        stratejik bir yorum üretir.
        """
        
        # PROMPT STRATEJİSİ: Kişisel veriyi "gizli" kullanarak tavsiye verdiriyoruz.
        prompt = f"""
        Sen "AlınırMı?" adlı bir finansal asistan ve akıllı alışveriş danışmanısın.
        
        GİRDİLER:
        - Ürün: {urun_verisi['urun_adi']}
        - Fiyat: {urun_verisi['fiyat']}
        - Yorumların Duygu Analizi Skoru: %{analiz_sonucu['oran']} {analiz_sonucu['durum']}
        - Kullanıcı Finansal Özeti: {kisisel_baglam} 
        
        GÖREVİN:
        1. Ürünün kalitesini ve risklerini model skoruna göre yorumla.
        2. Kullanıcının mevcut harcama alışkanlıklarına ve aboneliklerine göre bu harcamanın bütçeye etkisini değerlendir.
        3. Eğer bütçeye uymuyorsa veya ürün riskliyse, 'Sonraki Aylara Planla' tavsiyesi ver.
        4. Samimi ama profesyonel bir mühendis dili kullan.
        
        NOT:"Profiline baktığımda" gibi 
        doğrudan veri kaynağını belirten ifadeler ASLA kullanma. Tavsiyeyi doğal bir akışla ver.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"Danışman şu an meşgul: {str(e)}"

    def alternatif_ara(self, urun_adi):
        """Ürünün başka sitelerdeki fiyatlarını bulmak için arama yapar."""
        # Burada Google Search aracını tetikleyebiliriz.
        search_query = f"{urun_adi} en ucuz fiyat karşılaştırma"
        # ... arama sonuçlarını çekme mantığı ...
        return f"{urun_adi} için Google üzerinde güncel fiyat karşılaştırması yapılıyor..."