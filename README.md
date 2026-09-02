---
title: CartWise
emoji: 🛍️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# CartWise - Akıllı Alışveriş ve Finansal Karar Destek Asistanı

Bu proje, Trendyol ürün linklerini analiz ederek kullanıcı yorumlarının duygu analizini kendi eğittiğimiz PyTorch tabanlı bir Yapay Sinir Ağı (ANN) ile yapan ve Gemini API ile kullanıcının bütçesine özel akıllı alışveriş danışmanlığı sunan bir Flask web uygulamasıdır.

## Hugging Face Spaces Docker Dağıtımı

Bu dosyanın en üstündeki YAML metadata bloğu, Hugging Face'in bu projeyi bir **Docker** alanı (Space) olarak algılamasını ve `7860` portu üzerinden sunmasını sağlar.

## Yerel Geliştirme (Local Development)

Yerelde çalıştırmak için:
1. Gerekli kütüphaneleri kurun: `pip install -r requirements.txt`
2. `.env` dosyasını oluşturup değişkenleri tanımlayın:
   ```env
   GEMINI_API_KEY=your_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```
3. Uygulamayı çalıştırın: `python app.py`
