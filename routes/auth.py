from flask import Blueprint, request, redirect, url_for, session, render_template
import urllib.parse
from extensions import supabase

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    """Giriş sayfasını görüntüler."""
    if 'user' in session: 
        return redirect(url_for('analysis.ana_sayfa'))
    return render_template('login.html')

@auth_bp.route('/auth', methods=["POST"])
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
        session['user_email'] = res.user.email
        return redirect(url_for('analysis.ana_sayfa'))
    except Exception as e:
        return redirect(f"/login?error={urllib.parse.quote(str(e))}")
    

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login_page'))   