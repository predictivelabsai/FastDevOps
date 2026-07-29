from __future__ import annotations

import importlib.util
from pathlib import Path

from fasthtml.common import FastHTML, fast_app
from starlette.middleware.sessions import SessionMiddleware
from starlette.testclient import TestClient


TEMPLATE = Path(__file__).parents[1] / "templates/account_auth.py"


def load_module(tmp_path, monkeypatch):
    monkeypatch.setenv("FASTSME_AUTH_DB", str(tmp_path / "accounts.sqlite"))
    monkeypatch.setenv("FASTSME_PUBLIC_URL", "https://example.fastsme.com")
    monkeypatch.delenv("POSTMARK_API_TOKEN", raising=False)
    spec = importlib.util.spec_from_file_location("test_account_auth_module", TEMPLATE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_registration_requires_verification_and_supports_reset(tmp_path, monkeypatch):
    auth = load_module(tmp_path, monkeypatch)
    sent = []
    monkeypatch.setattr(auth.AccountStore, "_send_action",
                        lambda self, email, name, subject, action, token:
                        (sent.append((email, action, token)) or True))

    ok, message = auth.accounts.register("owner@example.com", "correct horse battery", "Owner")
    assert ok
    assert "verify" in message.lower()
    assert auth.accounts.login("owner@example.com", "correct horse battery") is None

    verification_token = sent[-1][2]
    account = auth.accounts.verify(verification_token)
    assert account["email"] == "owner@example.com"
    assert auth.accounts.verify(verification_token) is None
    assert auth.accounts.login("owner@example.com", "correct horse battery")

    auth.accounts.forgot("owner@example.com")
    reset_token = sent[-1][2]
    assert auth.accounts.reset(reset_token, "a newer secure password")
    assert not auth.accounts.reset(reset_token, "another secure password")
    assert auth.accounts.login("owner@example.com", "a newer secure password")


def test_google_link_is_verified_and_can_add_password_later(tmp_path, monkeypatch):
    auth = load_module(tmp_path, monkeypatch)
    account = auth.accounts.link_google("google@example.com", "Google User")
    assert account["is_verified"] == 1
    assert account["google_linked"] == 1
    assert auth.accounts.login("google@example.com", "not-set") is None


def test_registration_does_not_disclose_existing_verified_account(tmp_path, monkeypatch):
    auth = load_module(tmp_path, monkeypatch)
    tokens = []
    monkeypatch.setattr(auth.AccountStore, "_send_action",
                        lambda self, email, name, subject, action, token:
                        (tokens.append(token) or True))
    auth.accounts.register("person@example.com", "correct horse battery", "Person")
    auth.accounts.verify(tokens[-1])
    ok, message = auth.accounts.register("person@example.com", "different secure password", "Other")
    assert ok
    assert "already" not in message.lower()


def verified_account(auth, email="route@example.com"):
    captured = []
    auth.AccountStore._send_action = (
        lambda self, address, name, subject, action, token:
        (captured.append(token) or True)
    )
    auth.accounts.register(email, "correct horse battery", "Route User")
    auth.accounts.verify(captured[-1])


def test_fasthtml_route_adapter_establishes_session(tmp_path, monkeypatch):
    auth = load_module(tmp_path, monkeypatch)
    verified_account(auth)
    app, rt = fast_app(secret_key="test-secret")
    auth.register_fasthtml_routes(
        rt, app_name="Test", session_key="user", success_path="/inside"
    )
    client = TestClient(app)
    response = client.post(
        "/auth/local/login",
        data={"email": "route@example.com", "password": "correct horse battery"},
    )
    assert response.status_code == 200
    assert response.json()["redirect"] == "/inside"
    assert any(cookie.name.startswith("session") for cookie in client.cookies.jar)


def test_fastapi_route_adapter_establishes_session(tmp_path, monkeypatch):
    auth = load_module(tmp_path, monkeypatch)
    verified_account(auth)
    app = FastHTML()
    app.add_middleware(SessionMiddleware, secret_key="test-secret")
    auth.register_fastapi_routes(
        app, app_name="Test", session_key="user", success_path="/inside"
    )
    client = TestClient(app)
    response = client.post(
        "/auth/local/login",
        data={"email": "route@example.com", "password": "correct horse battery"},
    )
    assert response.status_code == 200
    assert response.json()["redirect"] == "/inside"
    assert any(cookie.name.startswith("session") for cookie in client.cookies.jar)
