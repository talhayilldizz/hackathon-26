from flask import Blueprint, request, redirect, url_for, session, render_template
from extensions import supabase
from flask import abort
from services.csrf import get_csrf_token, valid_csrf_token

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login_page():
    """Giriş sayfasını görüntüler."""
    if 'user' in session: 
        return redirect(url_for('analysis.ana_sayfa'))
    return render_template('login.html', csrf_token=get_csrf_token())

@auth_bp.route('/auth', methods=["POST"])
def auth_process():
    if not valid_csrf_token(request.form.get('csrf_token')):
        abort(403)

    email = request.form.get('email')
    pw = request.form.get('password')
    action = request.form.get('action')

    try:
        if action == 'register':
            res = supabase.auth.sign_up({"email": email, "password": pw})
            
            return redirect(url_for('auth.login_page', msg="Kayıt başarılı! Lütfen şimdi giriş yapın."))
            
        else:
            res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
            
            session['user'] = res.user.id
            session['user_email'] = res.user.email
            return redirect(url_for('analysis.ana_sayfa'))
            
    except Exception:
        return redirect(url_for(
            "auth.login_page",
            error="Giriş veya kayıt işlemi tamamlanamadı."
        ))
    

@auth_bp.route('/logout', methods=['POST'])
def logout():
    if 'user' not in session:
        return redirect(url_for('auth.login_page'))

    if not valid_csrf_token(request.form.get('csrf_token')):
        abort(403)

    session.clear()
    return redirect(url_for('auth.login_page'))   