import asyncio
import requests
import re
from urllib.parse import urlsplit
import time
from playwright.async_api import async_playwright

class TrendyolBot:
    def __init__(self):
        # Botun kimlik bilgileri ve genel ayarlari
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.trendyol.com/"
        }
        self.base_api_url = "https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/review-read/product-reviews/detailed"

    def linkten_id_al(self, url):
        """Yalnizca HTTPS Trendyol urun URL'lerinden ID ayiklar."""
        if not isinstance(url, str) or len(url) > 2048:
            return None

        if any(ord(char) <= 32 for char in url):
            return None

        try:
            parsed = urlsplit(url)

            if parsed.scheme != "https":
                return None

            if parsed.hostname not in {
                "trendyol.com",
                "www.trendyol.com",
            }:
                return None

            if (
                parsed.username is not None
                or parsed.password is not None
                or parsed.port is not None
            ):
                return None

            match = re.search(
                r"-p-([0-9]{1,20})/?$",
                parsed.path
            )

            return match.group(1) if match else None

        except ValueError:
            return None

    async def urun_bilgilerini_kazi(self, urun_url):
        """Playwright kullanarak urun adı, fiyat ve gorsel bilgilerini HTML'den ceker."""
        if not self.linkten_id_al(urun_url):
            raise ValueError("Gecersiz Trendyol urun adresi.")

        async with async_playwright() as p:
            tarayici = await p.chromium.launch(headless=True)
            baglam = await tarayici.new_context(user_agent=self.headers["User-Agent"])
            sayfa = await baglam.new_page()
            
            try:
                await sayfa.goto(urun_url, wait_until="domcontentloaded", timeout=60000)
                
                # Urun Adı
                ad_element = await sayfa.wait_for_selector("h1.product-title", timeout=5000)
                ad = await ad_element.inner_text() if ad_element else "Ad bulunamadi"
                
                # Fiyat Bilgisi
                fiyat_element = await sayfa.query_selector("span.discounted")
                if not fiyat_element:
                    fiyat_element = await sayfa.query_selector(".product-price")
                fiyat = await fiyat_element.inner_text() if fiyat_element else "Fiyat bulunamadi"
                
                # Gorsel URL
                gorsel_element = await sayfa.query_selector(".base-product-image img")
                gorsel_url = await gorsel_element.get_attribute("src") if gorsel_element else "Gorsel bulunamadi"

                await tarayici.close()
                return {
                    "urun_adi": ad.strip(),
                    "fiyat": fiyat.strip(),
                    "gorsel_url": gorsel_url
                }
            except Exception as e:
                print(f"HTML kazima sirasinda hata: {e}")
                await tarayici.close()
                return {"urun_adi": "Hata", "fiyat": "Hata", "gorsel_url": "Hata"}

    def yorumlari_cek(self, content_id):
        """Requests kullanarak urunun tum yorumlarini API üzerinden ceker."""
        tum_yorumlar = []
        mevcut_sayfa = 0
        toplam_sayfa = 1

        print(f"Sistem: {content_id} icin yorumlar toplaniyor...")

        while mevcut_sayfa < toplam_sayfa:
            api_sorgu_url = f"{self.base_api_url}?contentId={content_id}&page={mevcut_sayfa}&pageSize=20"
            try:
                cevap = requests.get(api_sorgu_url, headers=self.headers, timeout=10)
                if cevap.status_code == 200:
                    veri = cevap.json().get("result", {})
                    
                    if mevcut_sayfa == 0:
                        toplam_sayfa = veri.get("summary", {}).get("totalPages", 1)
                        print(f"Toplam {toplam_sayfa} sayfa yorum bulundu.")

                    yorumlar_listesi = veri.get("reviews", [])
                    for madde in yorumlar_listesi:
                        if madde.get("comment"):
                            tum_yorumlar.append({
                                "metin": madde["comment"].strip(),
                                "yildiz": madde.get("rate", 0)
                            })
                    
                    mevcut_sayfa += 1
                    time.sleep(0.3) # Rate limit korumasi
                else:
                    break
            except Exception as e:
                print(f"Yorum API hatasi: {e}")
                break
        
        return tum_yorumlar

    def alternatif_urunleri_cek(self, content_id):
        """Requests kullanarak verilen urune ait alternatif/benzer urun ID'lerini ceker."""
        # Belirttigin parametre yapısına uygun dinamik sorgu URL'si
        api_url = f"https://apigw.trendyol.com/discovery-storefront-trproductgw-service/api/reco-products/{content_id}?page=0&size=8&stampType=TypeA&sizeVariantAttributeValue=&isDynamicRendering=false&culture=tr-TR&recoType=similar&channelId=1"
        
        try:
            cevap = requests.get(api_url, headers=self.headers, timeout=10)
            if cevap.status_code == 200:
                veri = cevap.json().get("result", {})
                products = veri.get("products", [])
                
                # Sadece ürün ID'lerini string tipinde bir listede topluyoruz
                alternatif_urunler = {}

                for urun in products:
                    sozluk = {}
                    sozluk["name"] = urun.get("name")
                    sozluk["url"] = "https://www.trendyol.com" + urun.get("url")
                    sozluk["price"] = urun.get("prices").get("sellingPrice").get("value")
                    alternatif_urunler[str(urun.get("id"))] = sozluk

                return alternatif_urunler
        except Exception as e:
            print(f"Alternatif urun API hatasi: {e}")
            
        return []

    async def analiz_et(self, urun_url):
        """Botun ana calistirma fonksiyonu. Tum verileri birlestirip dict doner."""
        content_id = self.linkten_id_al(urun_url)
        if not content_id:
            return {"hata": "Gecersiz urun URL'si"}

        # 1. Adim: Urun temel bilgilerini kazi
        detaylar = await self.urun_bilgilerini_kazi(urun_url)
        
        # 2. Adim: Yorumlari API'den getir
        yorumlar = self.yorumlari_cek(content_id)
        
        # Yeni Adim: Alternatif/Benzer urunlerin ID listesini API'den getir
        alternatifler = self.alternatif_urunleri_cek(content_id)
        
        # 3. Adim: Sonuclari sozluk (dict) yapisinda birlestir
        sonuc_sozlugu = {
            "content_id": content_id,
            "urun_bilgisi": detaylar,
            "yorumlar": yorumlar,
            "toplam_yorum_sayisi": len(yorumlar),
            "alternatif_urunler": alternatifler, # Yeni eklenen ID listesi
            "islem_zamani": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return sonuc_sozlugu
    

bot = TrendyolBot()
# print(len(bot.alternatif_urunleri_cek(974364895)))
