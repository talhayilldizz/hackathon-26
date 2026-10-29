from google import genai
import json

class GeminiService:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview" 

    def finansal_danismanlik_yap(self, urun_verisi, analiz_sonucu, alternatifler,kisisel_baglam):
        """
        PyTorch modelinden gelen veriyi ve kullanıcı profilini birleştirip
        stratejik bir yorum üretir.
        """
        prompt = f"""
        Sen "CartWise" isimli bir finansal asistan ve akıllı alışveriş danışmanısın.
        Amacın, kullanıcıya bir ürünün hem finansal hem de kalite açısından mantıklı bir tercih olup olmadığını anlaşılır şekilde değerlendirmektir.

        # ÜRÜN BİLGİLERİ
        - Ürün Adı: {urun_verisi['urun_adi']}
        - Fiyat: {urun_verisi['fiyat']}
        - Alternatif Ürünler: {alternatifler}

        # YORUM ANALİZİ
        - Kullanıcı yorumlarının duygu analizi sonucu:
        %{analiz_sonucu['oran']} oranında {analiz_sonucu['durum']}

        # KULLANICI FİNANSAL DURUMU
        {kisisel_baglam}

        # GÖREVLERİN
        1. Ürünün genel kalite algısını yorum analizine göre değerlendir.
        2. Ürünün olası risklerini veya güçlü yönlerini belirt.
        3. Bu harcamanın kullanıcının mevcut bütçesi ve harcama alışkanlıkları açısından mantıklı olup olmadığını analiz et.
        4. Eğer ürün pahalı, riskli veya bütçeye uygun değilse:
        - Daha uygun fiyatlı alternatif öner isim, url ve fiyat ile birlikte.
        - veya satın almayı sonraki aylara erteleme tavsiyesi ver.
        5. Eğer ürün mantıklı görünüyorsa neden mantıklı olduğunu açıkla.

        # YAZIM KURALLARI
        - Samimi ama profesyonel konuş.
        - Kısa, net ve okunabilir paragraflar kullan.
        - Gereksiz tekrar yapma.
        - Kesin hüküm verme; olasılık odaklı konuş.
        - “Profiline baktığımda”, “Verilerine göre”, “Sistemde gördüğüm kadarıyla” gibi doğrudan veri kaynağını belli eden ifadeleri ASLA kullanma.
        - Tavsiyeleri doğal konuşma akışı içinde ver.
        
        NOT:"Profiline baktığımda" gibi 
        doğrudan veri kaynağını belirten ifadeler ASLA kullanma. Tavsiyeyi doğal bir akışla ver.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text
        except Exception:
            return "Danışman şu anda kullanılamıyor. Lütfen daha sonra tekrar deneyin."

    def alternatif_ara(self, urun_adi):
        """Ürünün başka sitelerdeki fiyatlarını bulmak için arama yapar."""
        # Burada Google Search aracını tetikleyebiliriz.
        search_query = f"{urun_adi} en ucuz fiyat karşılaştırma"
        # ... arama sonuçlarını çekme mantığı ...
        return f"{urun_adi} için Google üzerinde güncel fiyat karşılaştırması yapılıyor..."