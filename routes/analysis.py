from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from extensions import supabase
from services.model_service import ModelService
from services.trendyol_service import TrendyolBot
from services.gemini_service import GeminiService
import asyncio
from dotenv import load_dotenv
import os

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
        profil_verisi = profil_resp.data[0] if profil_resp.data else {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "email": session.get('user_email', '')}
    except:
        profil_verisi = {"isim": "", "soyisim": "", "gelir": 0, "gider": 0, "email": session.get('user_email', '')}

    return render_template('index.html', analizler=analizler, profil=profil_verisi)




load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
model_s = ModelService()
gemini_s = GeminiService(api_key=api_key)
bot = TrendyolBot()

@analysis_bp.route('/analiz', methods=['POST'])
def analiz_yap():
    """Yeni bir ürün analizi başlatır ve veritabanına kaydeder."""
    if 'user' not in session: return redirect(url_for('auth.login_page'))
    
    current_user_id = session.get('user')
    link = request.form.get("urun_linki")

    if not link:
        return redirect(url_for('analysis.ana_sayfa'))
    

    try:
        bot_verisi = asyncio.run(bot.analiz_et(link))
        model_analiz = model_s.toplu_analiz(bot_verisi["yorumlar"])
        profil_resp = supabase.table("profiles").select("*").eq("id", current_user_id).limit(1).execute()
        profil_data = profil_resp.data[0] if profil_resp.data else {}
        alternatifler = bot_verisi["alternatif_urunler"]

        finansal_baglam = f"Gelir: {profil_data.get('gelir', 0)} TL, Gider: {profil_data.get('gider', 0)} TL."

        gemini_yanit = gemini_s.finansal_danismanlik_yap(
            bot_verisi["urun_bilgisi"],
            model_analiz,
            alternatifler,
            finansal_baglam
        )

        
        gemini_yanit = gemini_yanit.strip()

        data = {
            "user_id" : current_user_id,
            "urun_linki" : link,
            "baslik" : request.form.get("baslik"),
            "model_skoru" : model_analiz["oran"],
            "model_sonucu" : model_analiz["durum"],
            "gemini_ozet" : gemini_yanit,
            "is_favorite":False,
            "status": "completed" if (gemini_yanit or model_analiz["oran"]) else "failed"
        }

        supabase.table("analizler").insert(data).execute()
        print(f"✅ Analiz Başarıyla Tamamlandı: {data['baslik']}")
        print(gemini_yanit)
    
    except Exception as e:
        print("❌ Analiz Hatası:", str(e))
        
    
    return redirect(url_for('analysis.ana_sayfa'))


@analysis_bp.route('/analiz_sil/<id>')
def analiz_sil(id): 
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