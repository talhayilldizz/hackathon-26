from flask import Blueprint, request, redirect, url_for, session, jsonify, abort
from extensions import supabase
from services.pdf_service import BankStatementAnalyzer
from services.csrf import valid_csrf_token
from dotenv import load_dotenv
import os
from tempfile import NamedTemporaryFile


profile_bp = Blueprint('profile', __name__)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
statement_analyzer = BankStatementAnalyzer(api_key)

@profile_bp.route('/profil_guncelle', methods=['POST'])
def profil_guncelle():
    if "user" not in session:
        return redirect(url_for("auth.login_page"))

    if not valid_csrf_token(request.form.get("csrf_token")):
        abort(403)

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
        print("Profil güncelleme hatası:", type(e).__name__)
        return redirect(url_for('analysis.ana_sayfa'))

MAX_PDF_BYTES = 10 * 1024 * 1024


@profile_bp.route('/profil/pdf_yukle', methods=['POST'])
def pdf_yukle():
    if "user" not in session:
        return jsonify({"error": "Oturum açmanız gerekiyor"}), 401

    if not valid_csrf_token(request.form.get("csrf_token")):
        abort(403)

    if "ekstre_pdf" not in request.files:
        return jsonify({"error": "Dosya seçilmedi"}), 400

    uploaded = request.files["ekstre_pdf"]

    if not uploaded.filename:
        return jsonify({"error": "Dosya adı boş"}), 400

    if not uploaded.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Yalnızca PDF yüklenebilir"}), 415

    content = uploaded.stream.read(MAX_PDF_BYTES + 1)

    if len(content) > MAX_PDF_BYTES:
        return jsonify({"error": "PDF boyutu 10 MB sınırını aşıyor"}), 413

    if not content.startswith(b"%PDF-"):
        return jsonify({"error": "Geçersiz PDF dosyası"}), 415

    temp_path = None

    try:
        with NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            prefix="cartwise-",
            delete=False,
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        sonuc = statement_analyzer.analiz_et(temp_path)

        if not sonuc:
            return jsonify({"error": "PDF analiz edilemedi"}), 500

        return jsonify(sonuc), 200

    except Exception:
        return jsonify({"error": "PDF işlenirken hata oluştu"}), 500

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
