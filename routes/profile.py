from flask import Blueprint, request, redirect, url_for, session
from extensions import supabase

profile_bp = Blueprint('profile', __name__)



@profile_bp.route('/profil_guncelle', methods=['POST'])
def profil_guncelle():
    if "user" not in session:
        return redirect("auth.login_page")
    

    try:
        gelir = int(request.form.get("gelir") or 0)
        gider = int(request.form.get("gider") or 0)
        hedef = int(request.form.get("hedef") or 0)

    except:
        gelir, gider, hedef = 0, 0, 0

    data = {
        "id" : session["user"],
        "isim" : request.form.get("isim"),
        "soyisim" : request.form.get("soyisim"),
        "email" : session.get("user_email"),
        "gelir" : gelir,
        "gider" : gider,
        "hedef" : hedef,
        "updated_at" : "now()"
    }

    try:
        supabase.table("profiles").upsert(data, on_conflict="id").execute()
        return redirect("/#profile") 
    except Exception as e:
        print("Profil Güncelleme Hatası:", str(e))
        return redirect(url_for('analysis.ana_sayfa'))