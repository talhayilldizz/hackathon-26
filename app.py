from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from supabase import create_client, Client
import urllib.parse

app = Flask(__name__)
# Güvenlik anahtarı: Oturum bilgilerini şifrelemek için kullanılır.
app.secret_key = "investwise_hackathon_premium_2024"

# ==========================================
# --- SUPABASE YAPILANDIRMASI ---
# ==========================================
url = "https://hereajktyvuktkwrbtev.supabase.co"
key = "sb_publishable_DXBiPAUNP2j0LdN4YYl1qA_WDP8ssrm"
supabase: Client = create_client(url, key)

# ==========================================
# --- ANA SAYFA VE GÖRÜNTÜLEME MANTIĞI ---
# ==========================================
@app.route('/')
def ana_sayfa():
    """
    Kullanıcıyı ana sayfaya yönlendirir, analizlerini ve profil verilerini çeker.
    Eğer URL'de ?view=ID varsa, o analizi en üste taşır.
    """
    if 'user' not in session: 
        return redirect(url_for('login_page'))
        
    current_user_id = session['user']
    view_id = request.args.get('view') # Geçmişten/Favoriden tıklanan analizi yakala
    
    try:
        # Kullanıcının tüm analizlerini kronolojik olarak getir
        analiz_resp = supabase.table("analizler").select("*").eq("user_id", current_user_id).order("created_at", desc=True).execute()
        analizler = analiz_resp.data
        
        # Eğer özel bir analiz görüntülenmek isteniyorsa, listede onu bul ve başa al
        if view_id and analizler:
            for i, analiz in enumerate(analizler):
                if str(analiz['id']) == str(view_id):
                    analizler.insert(0, analizler.pop(i))
                    break
    except:
        analizler = []
    
    try:
        # Kullanıcı bütçe ve isim bilgilerini çek
        profil_resp = supabase.table("profiles").select("*").eq("user_id", current_user_id).limit(1).execute()
        # Kayıt yoksa varsayılan boş şablonu kullan (Hata önleyici)
        profil_verisi = profil_resp.data[0] if profil_resp.data else {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "hedef": 0, "email": ""}
    except:
        profil_verisi = {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "hedef": 0, "email": ""}

    return render_template('index.html', analizler=analizler, profil=profil_verisi)

# ==========================================
# --- KİMLİK DOĞRULAMA (AUTH) İŞLEMLERİ ---
# ==========================================
@app.route('/login')
def login_page():
    """Giriş sayfasını görüntüler."""
    if 'user' in session: return redirect(url_for('ana_sayfa'))
    return render_template('login.html')

@app.route('/auth', methods=['POST'])
def auth_process():
    """Kayıt ve giriş işlemlerini Supabase Auth üzerinden yönetir."""
    email = request.form.get('email')
    pw = request.form.get('password')
    action = request.form.get('action')
    try:
        if action == 'register':
            res = supabase.auth.sign_up({"email": email, "password": pw})
        else:
            res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
        session['user'] = res.user.id
        return redirect(url_for('ana_sayfa'))
    except Exception as e:
        # Hata mesajını URL üzerinden giriş sayfasına geri gönder
        return redirect(f"/login?error={urllib.parse.quote(str(e))}")

@app.route('/logout')
def logout():
    """Kullanıcı oturumunu sonlandırır."""
    session.clear()
    return redirect(url_for('login_page'))

# ==========================================
# --- ANALİZ VE FAVORİ YÖNETİMİ ---
# ==========================================
@app.route('/analiz', methods=['POST'])
def analiz_yap():
    """Yeni bir ürün analizi başlatır ve veritabanına kaydeder."""
    if 'user' not in session: return redirect(url_for('login_page'))
    
    link = request.form.get('urun_linki')
    baslik = request.form.get('baslik')
    
    data = {
        "urun_linki": link,
        "baslik": baslik if baslik else "İsimsiz Ürün",
        "durum": "Analiz Ediliyor...", # Burası ileride AI skoruna göre değişecek
        "user_id": session['user'],
        "is_favorite": False
    }
    try:
        supabase.table("analizler").insert(data).execute()
    except:
        pass
    return redirect(url_for('ana_sayfa'))

@app.route('/analiz_sil/<id>')
def analiz_sil(id):
    """Belirli bir analizi veritabanından siler."""
    if 'user' not in session: return redirect(url_for('login_page'))
    try:
        supabase.table("analizler").delete().eq("id", id).eq("user_id", session['user']).execute()
    except:
        pass
    return redirect(url_for('ana_sayfa'))

@app.route('/api/favori_toggle/<id>/<status>', methods=['POST'])
def api_favori_toggle(id, status):
    """Favoriye ekleme/çıkarma işlemini sayfa yenilenmeden (AJAX) yapar."""
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    
    new_status = True if status == 'true' else False
    try:
        supabase.table("analizler").update({"is_favorite": new_status}).eq("id", id).eq("user_id", session['user']).execute()
        return jsonify({"success": True, "status": new_status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# --- PROFİL GÜNCELLEME ---
# ==========================================
@app.route('/profil_guncelle', methods=['POST'])
def profil_guncelle():
    """Kullanıcı bilgilerini ve bütçe verilerini Upsert yöntemiyle günceller."""
    if 'user' not in session: return redirect(url_for('login_page'))
    
    data = {
        "user_id": session['user'],
        "isim": request.form.get('isim'),
        "soyisim": request.form.get('soyisim'),
        "email": request.form.get('email'),
        "gelir": int(request.form.get('gelir') or 0),
        "gider": int(request.form.get('gider') or 0),
        "hedef": int(request.form.get('hedef') or 0)
    }
    try:
        # user_id çakışırsa güncelle, yoksa yeni kayıt aç
        supabase.table("profiles").upsert(data, on_conflict="user_id").execute()
        return redirect(f"/#profile") 
    except Exception as e:
        return redirect(url_for('ana_sayfa'))

if __name__ == '__main__':
    # Hackathon sunumunda portun çakışmaması için 5001 kullanıyoruz
    app.run(debug=True, port=5001)