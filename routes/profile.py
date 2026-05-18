from flask import Blueprint, request, redirect, url_for, session, jsonify
from extensions import supabase
from services.pdf_service import InvestWiseNative
from dotenv import load_dotenv
import os


profile_bp = Blueprint('profile', __name__)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
AI_MOTOR = InvestWiseNative(api_key)

@profile_bp.route('/profil_guncelle', methods=['POST'])
def profil_guncelle():
    if "user" not in session:
        return redirect(url_for("auth.login_page")) 

    try:
        # Form verilerini alırken hata payını sıfırlıyoruz
        gelir = int(request.form.get("gelir") or 0)
        gider = int(request.form.get("gider") or 0)
        # hedef = int(request.form.get("hedef") or 0)
    except (ValueError, TypeError):
        gelir, gider= 0, 0

    data = {
        "id" : session["user"],
        "isim" : request.form.get("isim"),
        "soyisim" : request.form.get("soyisim"),
        "email" : session.get("user_email"),
        "gelir" : gelir,
        "gider" : gider,
        "updated_at" : "now()"
    }

    try:
        supabase.table("profiles").upsert(data, on_conflict="id").execute()
        return redirect("/#profile") 
    except Exception as e:
        print("Profil Güncelleme Hatası:", str(e))
        return redirect(url_for('analysis.ana_sayfa'))

@profile_bp.route('/profil/pdf_yukle', methods=['POST'])
def pdf_yukle():
    if "user" not in session:
        return jsonify({"error": "Oturum açmanız gerekiyor"}), 401
    
    if 'ekstre_pdf' not in request.files:
        return jsonify({"error": "Dosya seçilmedi"}), 400
    
    file = request.files['ekstre_pdf']
    if file.filename == '':
        return jsonify({"error": "Dosya adı boş"}), 400

    try:
        temp_path = f"temp_{session['user']}.pdf"
        file.save(temp_path)
        sonuc = AI_MOTOR.analiz_et(temp_path)
    
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if sonuc:
            print(sonuc)
            return jsonify(sonuc), 200
        
        return jsonify({"error": "AI verileri okuyamadı"}), 500

    except Exception as e:
        print("PDF İşleme Hatası:", str(e))
        return jsonify({"error": f"Sunucu hatası: {str(e)}"}), 500