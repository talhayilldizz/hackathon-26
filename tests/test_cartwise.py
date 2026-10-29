import os
import secrets
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Testlerde gercek servis kimlik bilgilerini kullanma.
os.environ.update({
    "FLASK_SECRET_KEY": "cartwise-automated-test-only",
    "GEMINI_API_KEY": "dummy-test-key",
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_KEY": "dummy-test-key",
})

# Dis servis istemcilerini uygulama importundan once taklit et.
with patch("supabase.create_client"), patch("google.genai.Client"):
    from app import app
    from routes import analysis, auth
    from services.json_tokenizer import JsonTokenizer
    from services.trendyol_service import TrendyolBot


class CartWiseTests(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def login_session(self):
        token = secrets.token_urlsafe(32)
        with self.client.session_transaction() as session:
            session["user"] = "test-user"
            session["user_email"] = "test@example.com"
            session["_csrf_token"] = token
        return token

    def test_01_login_page(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)

        with self.client.session_transaction() as session:
            token = session["_csrf_token"]

        self.assertIn(
            f'value="{token}"',
            response.get_data(as_text=True)
        )

    def test_02_login_requires_csrf(self):
        response = self.client.post("/auth", data={
            "action": "login",
            "email": "test@example.com",
            "password": "dummy",
        })
        self.assertEqual(response.status_code, 403)

    def test_03_home_page(self):
        token = self.login_session()
        database = MagicMock()

        database.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        database.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = []

        with patch.object(
            analysis.supabase, "table", return_value=database
        ):
            response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f'value="{token}"',
            response.get_data(as_text=True)
        )

    def test_04_analysis_requires_csrf(self):
        self.login_session()
        response = self.client.post("/analiz", data={
            "urun_linki": "https://www.trendyol.com/urun-p-123"
        })
        self.assertEqual(response.status_code, 403)

    def test_05_favorite_requires_csrf(self):
        self.login_session()
        response = self.client.post(
            "/api/favori_toggle/123/true"
        )
        self.assertEqual(response.status_code, 403)

    def test_06_delete_requires_post_and_csrf(self):
        self.login_session()

        self.assertEqual(
            self.client.get("/analiz_sil/123").status_code,
            405
        )
        self.assertEqual(
            self.client.post("/analiz_sil/123").status_code,
            403
        )

    def test_07_logout_clears_session(self):
        token = self.login_session()

        self.assertEqual(
            self.client.get("/logout").status_code,
            405
        )

        response = self.client.post(
            "/logout",
            data={"csrf_token": token}
        )
        self.assertEqual(response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertNotIn("user", session)
            self.assertNotIn("_csrf_token", session)

    def test_08_pdf_requires_csrf(self):
        token = self.login_session()

        self.assertEqual(
            self.client.post("/profil/pdf_yukle").status_code,
            403
        )

        self.assertEqual(
            self.client.post(
                "/profil/pdf_yukle",
                data={"csrf_token": token}
            ).status_code,
            400
        )

    def test_09_tokenizer_reference(self):
        tokenizer = JsonTokenizer("models/tokenizer.json")

        result = tokenizer.texts_to_sequences([
            "Bu ürün gerçekten çok güzel",
            "Ürünün kalitesi oldukça kötü",
        ])

        self.assertEqual(result[0], [1, 8, 182, 5, 24])
        self.assertEqual(result[1], [212, 149, 423, 66])

    def test_10_pytorch_inference(self):
        score = analysis.model_s.tekli_tahmin(
            "Bu ürün gerçekten çok güzel"
        )

        self.assertGreaterEqual(float(score), 0)
        self.assertLessEqual(float(score), 1)

    def test_11_trendyol_url_validation(self):
        bot = TrendyolBot()

        self.assertEqual(
            bot.linkten_id_al(
                "https://www.trendyol.com/marka/urun-p-12345"
            ),
            "12345"
        )

        for url in [
            "http://127.0.0.1/urun-p-123",
            "https://trendyol.com.evil.test/urun-p-123",
            "file:///tmp/urun-p-123",
        ]:
            self.assertIsNone(bot.linkten_id_al(url))

    def test_12_logo_is_served(self):
        self.assertTrue(
            Path("static/cartwise-logo.svg").is_file()
        )

        response = self.client.get(
            "/static/cartwise-logo.svg"
        )

        try:
            self.assertEqual(response.status_code, 200)
        finally:
            response.close()


if __name__ == "__main__":
    unittest.main()
