from flask import Flask
from routes.auth import auth_bp
from routes.analysis import analysis_bp
from routes.profile import profile_bp

app = Flask(__name__)
app.secret_key = "investwise_hackathon_premium_2024"

# Blueprint'leri Kaydet 
app.register_blueprint(auth_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(profile_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001,use_reloader=False)