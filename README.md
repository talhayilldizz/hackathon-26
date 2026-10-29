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

# CartWise — AI-Powered Shopping & Financial Decision Assistant

CartWise, kullanıcıların alışveriş kararlarını ürün yorumları ve kişisel bütçeleriyle birlikte değerlendirmelerine yardımcı olan, Flask tabanlı bir web uygulamasıdır.

Trendyol ürün bağlantılarından alınan yorumlar, PyTorch ile geliştirilmiş bir duygu analizi modeliyle değerlendirilir. Google Gemini, ürün bilgilerini, analiz sonuçlarını ve kullanıcının sağladığı finansal bağlamı birleştirerek karar destek açıklamaları üretir.

> **Proje durumu:** Yerel model çıkarımı ve Flask'ın temel işlevleri test edilmiştir. Gerçek Supabase, Gemini, Trendyol ve Docker entegrasyonlarının uçtan uca doğrulaması henüz tamamlanmamıştır.

## Özellikler

- **Ürün analizi:** Trendyol ürün bağlantısından ürün bilgilerini ve müşteri yorumlarını toplama.
- **Duygu analizi:** PyTorch tabanlı yapay sinir ağıyla yorumların değerlendirilmesi.
- **AI danışmanlığı:** Gemini kullanılarak ürün ve bütçe verilerine dayalı açıklamalar oluşturulması.
- **Kullanıcı hesapları:** Supabase Authentication ile giriş ve kayıt.
- **Analiz geçmişi:** Kullanıcıya ait analizlerin kaydedilmesi, görüntülenmesi ve silinmesi.
- **Favoriler:** Analizlerin favorilere eklenmesi ve favorilerden çıkarılması.
- **Bütçe yönetimi:** Gelir ve gider bilgilerinin kullanıcı profilinde tutulması.
- **PDF analizi:** Kullanıcının yüklediği banka ekstresinden Gemini aracılığıyla finansal veriler çıkarılması.

## Teknolojiler

| Alan | Teknoloji |
|---|---|
| Backend | Python, Flask |
| Makine öğrenmesi | PyTorch |
| Metin ön işleme | JSON tabanlı tokenizer |
| Üretken yapay zekâ | Google Gemini API |
| Veritabanı ve kimlik doğrulama | Supabase |
| Web veri toplama | Playwright, Requests |
| Arayüz | HTML, CSS, JavaScript, Bootstrap |
| Dağıtım | Docker, Gunicorn |
| Model geliştirme | Jupyter Notebook |

## Sistem mimarisi

```text
Kullanıcı
   |
   v
Flask Web Uygulaması
   |
   +-- Supabase
   |     +-- Kullanıcı kimlik doğrulama
   |     +-- Profil ve analiz kayıtları
   |
   +-- Trendyol veri toplama
   |     +-- Ürün bilgileri
   |     +-- Müşteri yorumları
   |     +-- Alternatif ürün bilgileri
   |
   +-- PyTorch duygu analizi
   |     +-- tokenizer.json
   |     +-- sentiment_model.pth
   |
   +-- Gemini API
         +-- Alışveriş karar desteği
         +-- PDF ekstre analizi
```

## Proje yapısı

```text
cartwise/
├── app.py
├── extensions.py
├── routes/
│   ├── auth.py
│   ├── analysis.py
│   └── profile.py
├── services/
│   ├── csrf.py
│   ├── json_tokenizer.py
│   ├── model_service.py
│   ├── trendyol_service.py
│   ├── gemini_service.py
│   └── pdf_service.py
├── models/
│   ├── sentiment_model.pth
│   └── tokenizer.json
├── templates/
├── static/
├── notebooks/
├── requirements-prod.txt
├── requirements.txt
├── .env.example
└── Dockerfile
```

## Yerel kurulum

### 1. Sanal ortam oluşturun

Python 3.12 önerilir.

```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 2. Bağımlılıkları kurun

```bash
pip install -r requirements-prod.txt
python -m playwright install chromium
```

Model eğitimi ve notebook çalışmaları için ek geliştirme bağımlılıkları `requirements.txt` dosyasında bulunur.

### 3. Ortam değişkenlerini tanımlayın

```bash
cp .env.example .env
```

`.env` dosyasında aşağıdaki değişkenleri kendi bilgilerinizle yapılandırın:

```env
FLASK_SECRET_KEY=generate_a_secure_random_value
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_publishable_key
```

`FLASK_SECRET_KEY` için kriptografik olarak rastgele bir değer kullanın. Supabase üzerinde uygulamanın ihtiyaç duyduğu tabloların ve erişim politikalarının ayrıca yapılandırılması gerekir.

**Gerçek API anahtarlarını Git'e eklemeyin.** `.env` dosyası Git tarafından yok sayılır.

### 4. Uygulamayı çalıştırın

```bash
python app.py
```

Yerel Flask sunucusu varsayılan olarak `http://127.0.0.1:5001` adresinde başlar.

Gerçek ürün analizi ve hesap işlemleri için ilgili dış servislerin erişilebilir ve doğru yapılandırılmış olması gerekir.

## Docker ve Hugging Face Spaces

Proje, Docker ile dağıtılabilecek şekilde yapılandırılmıştır.

```bash
docker build -t cartwise .
docker run --rm -p 7860:7860 \
  --env-file .env \
  cartwise
```

Uygulama Gunicorn ile `7860` portundan sunulur. Hugging Face Spaces için gerekli Docker metadata bilgileri README dosyasının başında korunmaktadır.

**Not:** Docker yapılandırması güncellenmiştir ancak gerçek Docker build ve container çalışma testi henüz yapılmamıştır. Dağıtım ortamında gerekli servis anahtarlarının güvenli ortam değişkenleri veya secret yönetimi üzerinden sağlanması gerekir.

## Güvenlik ve veri gizliliği

Projede aşağıdaki önlemler bulunmaktadır:

- Flask oturum anahtarının ortam değişkeninden alınması.
- Geliştirme sunucusunda debug modunun kapalı tutulması.
- Form ve veri değiştiren isteklerde CSRF kontrolü.
- Analiz silme ve çıkış işlemlerinin yalnızca POST ile gerçekleştirilmesi.
- Analiz kayıtlarının kullanıcı kimliğine göre filtrelenmesi.
- Ürün bağlantılarında HTTPS ve Trendyol alan adı kontrolü.
- PDF yüklemelerinde 10 MB sınırı ve temel dosya imzası kontrolü.
- PDF işlemlerinde geçici dosyaların temizlenmesi.
- API hata ayrıntılarının kullanıcıya doğrudan gösterilmemesi.
- `.env` ve eski model dosyalarının Git/Docker kapsamından çıkarılması.

### Gizlilik uyarısı

PDF ekstre analizi etkinleştirildiğinde, kullanıcının yüklediği finansal belge Google Gemini API'ye gönderilir. Bu özelliğin üretim ortamında kullanılması öncesinde açık kullanıcı bilgilendirmesi, uygun veri işleme politikaları ve ilave dosya güvenliği kontrolleri gereklidir.

İlk URL doğrulaması, tarayıcı yönlendirmeleri veya alt kaynak isteklerinden doğabilecek bütün SSRF risklerini ortadan kaldırmaz. Dağıtım öncesinde ek ağ kısıtlamaları değerlendirilmelidir.

CartWise bir karar destek uygulamasıdır; finansal danışmanlık hizmeti sunmaz.

## Test durumu

### Otomatik testleri çalıştırma

Projenin kök dizininde, bağımlılıklar kurulduktan sonra:

```bash
python -m unittest discover -s tests -v
```

Bu testler gerçek Supabase ve Gemini anahtarları gerektirmez. Dış servisler taklit edilir; yerel PyTorch modeli gerçek çıkarım yapar.

Yerel geliştirme sırasında şu kontroller gerçekleştirilmiştir:

| Test | Durum |
|---|---|
| PyTorch model çıkarımı | Başarılı |
| JSON tokenizer eşdeğerlik kontrolü | Başarılı |
| Python modül importları | Başarılı |
| Flask yönlendirme ve oturum testleri | Başarılı |
| CSRF ve erişim kontrol testleri | Başarılı |
| PDF yükleme doğrulama testleri | Başarılı |
| Trendyol URL doğrulama testleri | Başarılı |
| Gerçek Supabase/Gemini entegrasyonu | Henüz doğrulanmadı |
| Gerçek Trendyol veri toplama | Henüz doğrulanmadı |
| Docker container çalıştırma | Henüz doğrulanmadı |

Testlerin bir bölümü dış servisler taklit edilerek (mock) yürütülmüştür. Bunlar gerçek servislerin uçtan uca çalıştığını kanıtlamaz.

## Bilinen sınırlamalar

- Trendyol sayfa yapısındaki ve API yanıtlarındaki değişiklikler veri toplama işlemini etkileyebilir.
- Ürün değerlendirmeleri, model tahminleri ve Gemini yanıtları hatalı veya eksik olabilir.
- PDF başlangıç imzasının kontrol edilmesi, dosyanın tamamen güvenli olduğunu garanti etmez.
- Gerçek dış servis entegrasyonları ve Docker dağıtımı için ek doğrulama gereklidir.

## Ekip ve katkılar

CartWise, bir hackathon kapsamında **ekip çalışması** olarak geliştirilmiştir.

Git geçmişinde katkıları bulunan geliştiriciler:

- **Talha Yildiz**
- **burak**
- **Emir Peker** (bazı eski commit'lerde `emir` adıyla)

Projenin ilk geliştirme süreci ve sonraki bakım, güvenlik ve belgelendirme çalışmaları aynı Git geçmişinde korunmaktadır. Her geliştiricinin katkıları commit kayıtlarından incelenebilir.

## Geliştirme

Proje, bir hackathon kapsamında ekip çalışması olarak geliştirilmiştir. Uygulama; makine öğrenmesi, veri toplama, web geliştirme ve üretken yapay zekâ bileşenlerini birleştirmektedir.
