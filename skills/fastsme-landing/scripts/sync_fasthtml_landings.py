#!/usr/bin/env python3
"""Synchronise shared landing and Google OAuth modules into FastHTML apps."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import yaml

SKILL_ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = SKILL_ROOT / "references/portfolio.yaml"


def find_control_plane() -> Path:
    """Find FastDevOps from either the control plane or a sibling Fast* repo."""
    cwd = Path.cwd().resolve()
    for parent in (cwd, *cwd.parents):
        if (parent / "config/services.yaml").is_file() and parent.name == "FastDevOps":
            return parent
        sibling = parent / "FastDevOps"
        if (sibling / "config/services.yaml").is_file():
            return sibling
    raise SystemExit("FastDevOps not found; run from FastDevOps or a sibling Fast* repository")


ROOT = find_control_plane()
FASTCO = ROOT.parent

LANDING_TEMPLATE = '''"""Public {name} product landing page."""
from urllib.parse import quote

from fasthtml.common import *

from .account_auth import AUTH_CSS, AUTH_JS, auth_modal

ACCENT = "{accent}"
TINT = "{tint}"
FAVICON = "data:image/svg+xml," + quote(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="{accent}"/><path fill="white" d="M16 4 28 16 16 28 4 16Z"/><path fill="{accent}" d="M11 10h11v4h-7v3h6v4h-6v5h-4Z"/></svg>""",
    safe="",
)

CSS = """
:root{{--accent:{accent};--tint:{tint};--ink:#111827;--muted:#667085;--line:#e7eaf0}}
*{{box-sizing:border-box}} body{{margin:0;background:#fff;color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}
.lp-nav{{height:68px;display:flex;align-items:center;justify-content:space-between;max-width:1180px;margin:auto;padding:0 24px;border-bottom:1px solid var(--line)}}
.lp-brand{{display:flex;align-items:center;gap:10px;font-weight:750;color:var(--ink);text-decoration:none}} .lp-mark{{width:30px;height:30px;border-radius:10px;background:var(--accent);display:grid;place-items:center;color:white}}
.lp-signin,.lp-primary{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:10px 17px;text-decoration:none;font-weight:650;font-size:14px;cursor:pointer}} .lp-signin{{border:1px solid var(--line);color:var(--ink);background:white}} .lp-primary{{background:var(--accent);color:white;border:0}}
.lp-hero{{max-width:1180px;margin:auto;padding:104px 24px 76px}} .lp-kicker{{color:var(--accent);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.16em}}
.lp-hero h1{{font-size:clamp(42px,7vw,78px);line-height:1.02;letter-spacing:-.055em;max-width:920px;margin:22px 0}} .lp-lede{{font-size:20px;line-height:1.65;color:var(--muted);max-width:720px}}
.lp-actions{{display:flex;gap:12px;margin-top:32px;flex-wrap:wrap}} .lp-secondary{{color:var(--ink);font-weight:650;text-decoration:none;padding:10px 4px}}
.lp-demo{{max-width:960px;margin:0 auto 76px;padding:0 24px}} .lp-demo-frame{{padding:10px;background:#fff;border:1px solid var(--line);border-radius:22px;box-shadow:0 24px 70px rgba(17,24,39,.10)}}
.lp-demo img{{display:block;width:100%;height:auto;border-radius:14px;background:var(--tint)}} .lp-demo p{{margin:13px 0 2px;text-align:center;color:var(--muted);font-size:13px}}
.lp-band{{background:var(--tint);border-block:1px solid color-mix(in srgb,var(--accent) 15%,white)}} .lp-grid{{max-width:1180px;margin:auto;padding:64px 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.lp-card{{background:rgba(255,255,255,.82);border:1px solid color-mix(in srgb,var(--accent) 15%,white);border-radius:20px;padding:26px}} .lp-num{{color:var(--accent);font-size:12px;font-weight:750}} .lp-card h2{{font-size:20px;margin:24px 0 8px}} .lp-card p{{color:var(--muted);line-height:1.6;margin:0}}
.lp-footer{{max-width:1180px;margin:auto;padding:30px 24px 48px;color:var(--muted);font-size:13px;display:flex;justify-content:space-between;gap:20px}}
@media(max-width:760px){{.lp-nav{{height:60px}}.lp-hero{{padding-top:72px}}.lp-grid{{grid-template-columns:1fr}}.lp-footer{{flex-direction:column}}}}
"""

def landing_page():
    features = {features!r}
    return Html(
        Head(Title("{name} · FastSME"), Meta(charset="utf-8"),
             Meta(name="viewport", content="width=device-width, initial-scale=1"),
             Meta(name="description", content="{description}"),
             Link(rel="icon", type="image/svg+xml", href=FAVICON),
             Link(rel="preconnect", href="https://fonts.googleapis.com"),
             Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;750&display=swap"),
             Style(CSS + AUTH_CSS)),
        Body(
            Nav(A(Span("F", cls="lp-mark"), Span("{name}"), href="/", cls="lp-brand"),
                Button("Sign In", type="button", onclick="authOpen('login')", cls="lp-signin"), cls="lp-nav"),
            Main(
                Section(Span("{eyebrow}", cls="lp-kicker"), H1("{headline}"),
                        P("{description}", cls="lp-lede"),
                        Div(Button("Sign In or Register", type="button", onclick="authOpen('login')", cls="lp-primary"),
                            A("Explore the open-source suite →", href="https://fastsme.com/products", cls="lp-secondary"),
                            cls="lp-actions"), cls="lp-hero"),
                Section(Div(Img(src="/static/product-demo.gif", alt="{name} product tour",
                                loading="eager", width="1854", height="909"),
                            P("Product tour · see the workspace in action"),
                            cls="lp-demo-frame"), cls="lp-demo", aria_label="{name} product tour"),
                Section(Div(*[Article(Span(f"0{{i}}", cls="lp-num"), H2(title),
                                      P("Everything you need for " + title.lower() + ", in one focused workspace."),
                                      cls="lp-card") for i, title in enumerate(features, 1)],
                            cls="lp-grid"), cls="lp-band"),
            ),
            Footer(Span("{name} is part of the open-source FastSME suite."),
                   A("View all products", href="https://fastsme.com/products", style="color:var(--accent)"),
                   cls="lp-footer"),
            auth_modal("{name}"),
            Script(AUTH_JS),
        ),
    )
'''

OAUTH_MODULE = '''"""Minimal server-side Google OpenID Connect flow."""
from __future__ import annotations
import json, os, secrets
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

def enabled(): return bool(CLIENT_ID and CLIENT_SECRET)
def new_state(): return secrets.token_urlsafe(32)

def callback_uri(request):
    if REDIRECT_URI: return REDIRECT_URI
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    return f"{proto}://{host}/auth/google/callback"

def authorize_url(request, state):
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": CLIENT_ID, "redirect_uri": callback_uri(request),
        "response_type": "code", "scope": "openid email profile",
        "state": state, "access_type": "online", "prompt": "select_account"})

def _json_request(url, *, data=None, token=None):
    body = urlencode(data).encode() if data else None
    headers = {"Accept": "application/json"}
    if data: headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token: headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(url, data=body, headers=headers), timeout=20) as response:
        return json.loads(response.read())

def exchange(request, code):
    try:
        token = _json_request("https://oauth2.googleapis.com/token", data={
            "code": code, "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
            "redirect_uri": callback_uri(request), "grant_type": "authorization_code"})
        info = _json_request("https://openidconnect.googleapis.com/v1/userinfo",
                             token=token.get("access_token"))
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None
    email = (info.get("email") or "").strip().lower()
    if not email or info.get("email_verified") is False: return None
    domains = {x.strip().lower() for x in os.getenv("GOOGLE_ALLOWED_DOMAINS", "").split(",") if x.strip()}
    emails = {x.strip().lower() for x in os.getenv("GOOGLE_ALLOWED_EMAILS", "").split(",") if x.strip()}
    if domains or emails:
        if email not in emails and email.rsplit("@", 1)[-1] not in domains: return None
    return {"email": email, "name": info.get("name") or email}
'''

IMPORT_MARKER = "from web import views, ai"
ROUTES = '''

@rt("/auth/google")
def google_start(session, request):
    if not google_auth.enabled():
        return RedirectResponse("/login?error=Google+sign-in+is+not+configured", status_code=303)
    state = google_auth.new_state()
    session["google_oauth_state"] = state
    return RedirectResponse(google_auth.authorize_url(request, state), status_code=303)


@rt("/auth/google/callback")
def google_callback(session, request, code: str = "", state: str = "", error: str = ""):
    if error or not code or state != session.pop("google_oauth_state", None):
        return RedirectResponse("/login?error=Google+sign-in+failed", status_code=303)
    identity = google_auth.exchange(request, code)
    if not identity:
        return RedirectResponse("/login?error=Google+account+is+not+authorised", status_code=303)
    session["user"] = identity["email"]
    return RedirectResponse("{success}", status_code=303)
'''


def sync_app(name: str, meta: dict, check: bool) -> list[str]:
    repo = FASTCO / name
    custom_paths = {
        "FastFunnel": "fastfunnel/web/landing.py",
        "FastCMS": "app/landing.py",
        "FastFund": "web/landing.py",
        "FastLMS": "components/landing.py",
        "FastPPM": "web/landing.py",
    }
    demo_source = repo / meta["demo_gif"]
    demo_target = repo / "static/product-demo.gif"
    asset_changes = []
    if not demo_source.is_file():
        raise SystemExit(f"{name}: missing demo GIF: {demo_source.relative_to(repo)}")
    if not demo_target.is_file() or demo_target.read_bytes() != demo_source.read_bytes():
        asset_changes.append(str(demo_target.relative_to(repo)))
        if not check:
            demo_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(demo_source, demo_target)
    if meta.get("cohort") == "streamlit":
        return asset_changes
    if meta.get("cohort") == "custom":
        path = repo / custom_paths[name]
        expected = LANDING_TEMPLATE.format(name=name, **meta)
        oauth_path = path.with_name("google_auth.py")
        account_path = path.with_name("account_auth.py")
        changed = asset_changes
        if not path.exists() or path.read_text() != expected:
            if not check:
                path.write_text(expected)
            changed.append(str(path.relative_to(repo)))
        if name in {"FastFunnel", "FastCMS", "FastLMS"} and (
                not oauth_path.exists() or oauth_path.read_text() != OAUTH_MODULE):
            if not check:
                oauth_path.write_text(OAUTH_MODULE)
            changed.append(str(oauth_path.relative_to(repo)))
        expected_account = (SKILL_ROOT / "templates/account_auth.py").read_text()
        if not account_path.exists() or account_path.read_text() != expected_account:
            if not check:
                account_path.write_text(expected_account)
            changed.append(str(account_path.relative_to(repo)))
        sample = repo / ".env.sample"
        if not sample.exists():
            sample = repo / ".env.example"
        if sample.exists() and "FASTSME_AUTH_DB=" not in sample.read_text():
            addition = (
                "\n# FastSME local accounts and transactional email\n"
                "FASTSME_AUTH_DB=\n"
                f"FASTSME_PUBLIC_URL=https://{meta['slug']}.fastsme.com\n"
                "POSTMARK_API_TOKEN=\n"
                "FROM_EMAIL=info@predictivelabs.ai\n"
            )
            if not check:
                sample.write_text(sample.read_text().rstrip() + "\n" + addition)
            changed.append(sample.name)
        elif sample.exists() and "FROM_EMAIL=info@predictivelabs.co.uk" in sample.read_text():
            if not check:
                sample.write_text(sample.read_text().replace(
                    "FROM_EMAIL=info@predictivelabs.co.uk",
                    "FROM_EMAIL=info@predictivelabs.ai",
                ))
            changed.append(sample.name)
        return changed
    app_path = repo / "web_app.py"
    landing_path = repo / "web/landing.py"
    oauth_path = repo / "web/google_auth.py"
    account_path = repo / "web/account_auth.py"
    changes = asset_changes
    expected_landing = LANDING_TEMPLATE.format(name=name, **meta)
    expected_account = (SKILL_ROOT / "templates/account_auth.py").read_text()
    for path, expected in ((landing_path, expected_landing), (oauth_path, OAUTH_MODULE),
                           (account_path, expected_account)):
        if not path.exists() or path.read_text() != expected:
            changes.append(str(path.relative_to(repo)))
            if not check:
                path.write_text(expected)

    source = app_path.read_text()
    updated = source
    if "from web.landing import landing_page" not in updated:
        if name == "FastClinic":
            marker = "from web.layout import page, right_pane_reference, LAYOUT_CSS"
        else:
            marker = IMPORT_MARKER if IMPORT_MARKER in updated else "from web import views"
        updated = updated.replace(marker, marker + "\nfrom web.landing import landing_page\nfrom web import account_auth, google_auth", 1)
    elif "from web import google_auth" in updated and "account_auth" not in updated:
        updated = updated.replace("from web import google_auth", "from web import account_auth, google_auth", 1)
    if "account_auth.register_fasthtml_routes(" not in updated:
        session_key = "user_email" if name == "FastClinic" else "user"
        success = "/role-select" if name == "FastESM" else "/"
        marker = "def _auth" if name == "FastClinic" else "def _user"
        registration = (
            f'account_auth.register_fasthtml_routes(rt, app_name="{name}", '
            f'session_key="{session_key}", success_path="{success}")\n\n\n'
        )
        updated = updated.replace(marker, registration + marker, 1)
    updated = updated.replace(
        '")\\n\\n\\n# --- auth helpers',
        '")\n\n\n# --- auth helpers',
    )
    if '@rt("/auth/google")' not in updated:
        success = "/role-select" if name == "FastESM" else "/"
        block = ROUTES.format(success=success)
        updated = updated.replace("\n@rt(\"/logout\")", block + "\n\n@rt(\"/logout\")", 1)
    if "account_auth.accounts.link_google" not in updated:
        session_assignment = (
            '    session["user_email"] = identity["email"]'
            if name == "FastClinic" else
            '    session["user"] = identity["email"]'
        )
        updated = updated.replace(
            session_assignment,
            '    account_auth.accounts.link_google(identity["email"], identity["name"])\n'
            + session_assignment,
            1,
        )
    updated = updated.replace(
        'identity["name"])\\n    session["user"]',
        'identity["name"])\n    session["user"]',
    )
    root_marker = '@rt("/")\ndef get(session'
    start = updated.find(root_marker)
    if start >= 0:
        body_start = updated.find("\n", updated.find("):", start)) + 1
        if "landing_page()" not in updated[body_start:body_start + 180]:
            auth_fn = "_auth" if name == "FastClinic" else "_user"
            updated = updated[:body_start] + f"    if not {auth_fn}(session):\n        return landing_page()\n" + updated[body_start:]
    if name == "FastClinic":
        updated = updated.replace(
            '    session["user"] = identity["email"]\n    return RedirectResponse("/", status_code=303)',
            '    session["user_email"] = identity["email"]\n    return RedirectResponse("/", status_code=303)',
            1,
        )
        updated = updated.replace(
            "    if not _user(session):\n        return landing_page()",
            "    if not _auth(session):\n        return landing_page()",
            1,
        )
    if updated != source:
        changes.append(str(app_path.relative_to(repo)))
        if not check:
            app_path.write_text(updated)

    sample = repo / ".env.sample"
    if not sample.exists():
        sample = repo / ".env.example"
    if sample.exists():
        text = sample.read_text()
        if "GOOGLE_CLIENT_ID=" not in text:
            addition = (
                "\n# Google SSO\nGOOGLE_CLIENT_ID=\nGOOGLE_CLIENT_SECRET=\n"
                f"GOOGLE_REDIRECT_URI=https://{meta['slug']}.fastsme.com/auth/google/callback\n"
                "GOOGLE_ALLOWED_DOMAINS=\nGOOGLE_ALLOWED_EMAILS=\n"
                "FASTSME_AUTH_DB=\nFASTSME_PUBLIC_URL=\nPOSTMARK_API_TOKEN=\nFROM_EMAIL=\n"
            )
            changes.append(sample.name)
            if not check:
                sample.write_text(text.rstrip() + "\n" + addition)
                text = sample.read_text()
        if "FASTSME_AUTH_DB=" not in text:
            addition = (
                "\n# FastSME local accounts and transactional email\n"
                "FASTSME_AUTH_DB=\n"
                f"FASTSME_PUBLIC_URL=https://{meta['slug']}.fastsme.com\n"
                "POSTMARK_API_TOKEN=\n"
                "FROM_EMAIL=info@predictivelabs.ai\n"
            )
            changes.append(sample.name)
            if not check:
                sample.write_text(text.rstrip() + "\n" + addition)
        elif "FROM_EMAIL=info@predictivelabs.co.uk" in text:
            changes.append(sample.name)
            if not check:
                sample.write_text(text.replace(
                    "FROM_EMAIL=info@predictivelabs.co.uk",
                    "FROM_EMAIL=info@predictivelabs.ai",
                ))
    return changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    apps = yaml.safe_load(PORTFOLIO.read_text())["apps"]
    drift = {}
    for name, meta in apps.items():
        changed = sync_app(name, meta, args.check)
        if changed:
            drift[name] = changed
    for name, files in drift.items():
        print(f"{name}: {', '.join(files)}")
    if args.check and drift:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
