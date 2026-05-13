from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from extensions import supabase

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/')
def ana_sayfa():
    if 'user' not in session:
        return redirect(url_for('auth.login_page'))
    
    current_user_id = session['user']
    view_id = request.args.get('view') # Geçmişten/Favoriden tıklanan analizi yakala
    

    try:
        analiz_resp = supabase.table("analizler").select("*").eq("user_id", current_user_id).order("created_at", desc=True).execute()
        analizler = analiz_resp.data

        if view_id and analizler:
            for i, analiz in enumerate(analizler):
                if str(analiz['id']) == str(view_id):
                    analizler.insert(0, analizler.pop(i))
                    break

    except:
        analizler = []

    try:
        profil_resp = supabase.table("profiles").select("*").eq("id", current_user_id).limit(1).execute()
        profil_verisi = profil_resp.data[0] if profil_resp.data else {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "hedef": 0, "email": session.get('user_email', '')}
    except:
        profil_verisi = {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "hedef": 0, "email": session.get('user_email', '')}

    return render_template('index.html', analizler=analizler, profil=profil_verisi)



@analysis_bp.route('/analiz', methods=['POST'])
def analiz_yap():
    """Yeni bir ürün analizi başlatır ve veritabanına kaydeder."""
    if 'user' not in session: return redirect(url_for('auth.login_page'))
    

    link = request.form.get("urun_linki")
    baslik = request.form.get("baslik")
    tahmin_skoru = None
    tahmin_sonucu = ""
    gemini_yanit = ""

    data = {
        "user_id": session.get("user"),
        "urun_linki": link if link else "Link belirtilmedi",
        "baslik": baslik if baslik else "İsimsiz Ürün",
        "model_skoru": tahmin_skoru if tahmin_skoru is not None else 0.5,
        "model_sonucu": tahmin_sonucu if tahmin_sonucu else "BELİRSİZ",
        "gemini_ozet": gemini_yanit if gemini_yanit else "Yapay zeka analizi hazırlanıyor veya hata oluştu.",
        "is_favorite": False,
        "status": "completed" if (gemini_yanit or tahmin_skoru) else "failed"
    }

    try:
        supabase.table("analizler").insert(data).execute()
    except Exception as e:
        print("Analiz Kayıt Hatası:", str(e))
    return redirect(url_for('analysis.ana_sayfa'))

@analysis_bp.route('/analiz_sil/<id>')
def analiz_sil(id): # ...o yüzden burada parantez içine 'id' yazmak ZORUNDAYIZ.
    """Belirli bir analizi veritabanından siler."""
    if 'user' not in session: 
        return redirect(url_for('auth.login_page'))
        
    try:
        # Supabase'den silme işlemi
        supabase.table("analizler").delete().eq("id", id).eq("user_id", session['user']).execute()
        print(f"✅ Analiz {id} başarıyla silindi.")
    except Exception as e:
        print("❌ Silme Hatası:", str(e))
        
    return redirect(url_for('analysis.ana_sayfa'))

@analysis_bp.route('/api/favori_toggle/<id>/<status>', methods=['POST'])
def api_favori_toggle(id, status):
    if 'user' not in session: return jsonify({"error": "Unauthorized"}), 401
    new_status = True if status == 'true' else False
    try:
        supabase.table("analizler").update({"is_favorite": new_status}).eq("id", id).eq("user_id", session['user']).execute()
        return jsonify({"success": True})
    except: return jsonify({"error": "DB Error"}), 500