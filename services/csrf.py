import secrets
from flask import session


def get_csrf_token():
    token = session.get("_csrf_token")
    if not isinstance(token, str) or len(token) < 20:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def valid_csrf_token(candidate):
    expected = session.get("_csrf_token")
    return (
        isinstance(expected, str)
        and isinstance(candidate, str)
        and secrets.compare_digest(expected, candidate)
    )
