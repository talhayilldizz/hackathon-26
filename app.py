from flask import Flask
from routes.auth import auth_bp
from routes.analysis import analysis_bp
from routes.profile import profile_bp

import os

app = Flask(__name__)
secret_key = os.environ.get("FLASK_SECRET_KEY")
if not secret_key:
    raise RuntimeError("FLASK_SECRET_KEY must be configured.")

app.secret_key = secret_key

# Blueprint'leri Kaydet 
app.register_blueprint(auth_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(profile_bp)

if __name__ == '__main__':
    app.run(debug=False, port=5001, use_reloader=False)