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
from .seo import seo_meta

ACCENT = "{accent}"
TINT = "{tint}"
FAVICON = "data:image/svg+xml," + quote(
    """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="{accent}"/><path fill="white" d="M16 4 28 16 16 28 4 16Z"/><path fill="{accent}" d="M11 10h11v4h-7v3h6v4h-6v5h-4Z"/></svg>""",
    safe="",
)

PARTNERS = (
    ("SAASPASS", "https://saaspass.com/", "https://saaspass.com/_next/static/assets/0176aeff921f6359fee88e796be31ace.png", "Full-stack identity and access management spanning MFA, SSO, passwordless access and integration APIs."),
    ("Sixty Four", "https://sixtyfour.ee/", "https://sixtyfour.ee/favicon.ico", "A senior Tallinn technology studio delivering software, AI consultancy, service design and public-sector programmes."),
    ("EDI Labs", "https://edilabs.tech/", "https://edilabs.tech/static/favicon.svg", "AI and data engineering for document intelligence, forecasting, geospatial systems and agentic workflows."),
    ("Predictive Labs", "https://predictivelabs.ai/", "https://predictivelabs.ai/static/favicon.svg", "Auditable AI systems for health, defence, public management, mobility and financial services."),
    ("Consistente", "https://consistente.tech/", "https://consistente.tech/static/favicon.svg", "Enterprise AI delivery across financial services, healthcare, the public sector and technology."),
    ("Manmouna Technologies", "https://manmouna.tech/", "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='16' fill='%230B1E14'/%3E%3Cpath d='M32 12 52 32 32 52 12 32Z' fill='%2334D399'/%3E%3Cpath d='M32 22 42 32 32 42 22 32Z' fill='%230B1E14'/%3E%3C/svg%3E", "Auditable-by-design AI systems for European public services across health, defence, public management and mobility."),
)

CSS = """
:root{{--accent:{accent};--tint:{tint};--ink:#111827;--muted:#667085;--line:#e7eaf0}}
*{{box-sizing:border-box}} body{{margin:0;background:#fff;color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}
.lp-nav{{height:68px;display:flex;align-items:center;justify-content:space-between;max-width:1180px;margin:auto;padding:0 24px;border-bottom:1px solid var(--line)}}
.lp-brand{{display:flex;align-items:center;gap:10px;font-weight:750;color:var(--ink);text-decoration:none}} .lp-mark{{width:30px;height:30px;border-radius:10px;background:var(--accent);display:grid;place-items:center;color:white}}
.lp-nav-actions{{display:flex;align-items:center;gap:18px}} .lp-nav-link{{color:var(--muted);text-decoration:none;font-size:14px;font-weight:650}} .lp-nav-link:hover{{color:var(--accent)}}
.lp-signin,.lp-primary{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:10px 17px;text-decoration:none;font-weight:650;font-size:14px;cursor:pointer}} .lp-signin{{border:1px solid var(--line);color:var(--ink);background:white}} .lp-primary{{background:var(--accent);color:white;border:0}}
.lp-hero{{max-width:1180px;margin:auto;padding:104px 24px 76px}} .lp-kicker{{color:var(--accent);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.16em}}
.lp-hero h1{{font-size:clamp(42px,7vw,78px);line-height:1.02;letter-spacing:-.055em;max-width:920px;margin:22px 0}} .lp-lede{{font-size:20px;line-height:1.65;color:var(--muted);max-width:720px}}
.lp-actions{{display:flex;gap:12px;margin-top:32px;flex-wrap:wrap}} .lp-secondary{{color:var(--ink);font-weight:650;text-decoration:none;padding:10px 4px}}
.lp-demo{{max-width:960px;margin:0 auto 76px;padding:0 24px}} .lp-demo-frame{{padding:10px;background:#fff;border:1px solid var(--line);border-radius:22px;box-shadow:0 24px 70px rgba(17,24,39,.10)}}
.lp-demo img{{display:block;width:100%;height:auto;border-radius:14px;background:var(--tint)}} .lp-demo p{{margin:13px 0 2px;text-align:center;color:var(--muted);font-size:13px}}
.lp-band{{background:var(--tint);border-block:1px solid color-mix(in srgb,var(--accent) 15%,white)}} .lp-grid{{max-width:1180px;margin:auto;padding:64px 24px;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
.lp-card{{background:rgba(255,255,255,.82);border:1px solid color-mix(in srgb,var(--accent) 15%,white);border-radius:20px;padding:26px}} .lp-num{{color:var(--accent);font-size:12px;font-weight:750}} .lp-card h2{{font-size:20px;margin:24px 0 8px}} .lp-card p{{color:var(--muted);line-height:1.6;margin:0}}
.lp-partners{{max-width:1180px;margin:auto;padding:72px 24px;scroll-margin-top:80px}} .lp-partners-head{{max-width:720px}} .lp-partners-head h2{{font-size:32px;letter-spacing:-.03em;margin:10px 0 12px}} .lp-partners-head p{{color:var(--muted);line-height:1.65;margin:0}}
.lp-partner-grid{{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin-top:32px}} .lp-partner{{min-width:0;color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:18px;padding:20px;background:#fff;transition:transform .18s,border-color .18s,box-shadow .18s}} .lp-partner:hover{{transform:translateY(-3px);border-color:color-mix(in srgb,var(--accent) 40%,white);box-shadow:0 14px 34px rgba(17,24,39,.08)}}
.lp-partner-top{{display:flex;align-items:center;justify-content:space-between;gap:12px}} .lp-partner-logo{{width:46px;height:46px;object-fit:contain}} .lp-partner-type{{color:var(--accent);font-size:10px;font-weight:750;text-transform:uppercase;letter-spacing:.1em;text-align:right}} .lp-partner h3{{font-size:18px;margin:18px 0 8px}} .lp-partner p{{color:var(--muted);font-size:13px;line-height:1.55;margin:0}} .lp-partner-visit{{display:block;color:var(--accent);font-size:12px;font-weight:700;margin-top:16px}}
.lp-developers{{max-width:1180px;margin:auto;padding:72px 24px;display:grid;grid-template-columns:1fr auto;align-items:center;gap:32px}} .lp-developers h2{{font-size:32px;letter-spacing:-.03em;margin:8px 0 12px}} .lp-developers p{{color:var(--muted);line-height:1.65;max-width:680px;margin:0}}
.lp-footer{{max-width:1180px;margin:auto;padding:30px 24px 48px;color:var(--muted);font-size:13px;display:flex;justify-content:space-between;gap:20px}}
@media(max-width:980px){{.lp-partner-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
@media(max-width:760px){{.lp-nav{{height:60px}}.lp-nav-actions{{gap:10px}}.lp-nav-actions .lp-nav-link:nth-child(2){{display:none}}.lp-nav-link{{font-size:13px}}.lp-hero{{padding-top:72px}}.lp-grid,.lp-partner-grid{{grid-template-columns:1fr}}.lp-developers{{grid-template-columns:1fr}}.lp-footer{{flex-direction:column}}}}
"""

def partner_section():
    return Section(
        Div(
            Span("Partners", cls="lp-kicker"),
            H2("Connect with trusted integration specialists."),
            P("Identity, software delivery, data engineering and applied-AI expertise for FastSME implementations."),
            cls="lp-partners-head",
        ),
        Div(*[
            A(
                Div(Img(src=logo, alt=f"{{name}} logo", loading="lazy", cls="lp-partner-logo"),
                    Span("Integration Partner", cls="lp-partner-type"), cls="lp-partner-top"),
                H3(name), P(description), Span("Visit website ↗", cls="lp-partner-visit"),
                href=url, target="_blank", rel="noopener noreferrer", cls="lp-partner",
            )
            for name, url, logo, description in PARTNERS
        ], cls="lp-partner-grid"),
        id="partners", cls="lp-partners",
    )

def landing_page():
    features = {features!r}
    return Html(
        Head(Title("{name} · FastSME"), Meta(charset="utf-8"),
             Meta(name="viewport", content="width=device-width, initial-scale=1"),
             Meta(name="description", content="{description}"),
             *seo_meta(),
             Link(rel="icon", type="image/svg+xml", href=FAVICON),
             Link(rel="preconnect", href="https://fonts.googleapis.com"),
             Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;750&display=swap"),
             Style(CSS + AUTH_CSS)),
        Body(
            Nav(A(Span("F", cls="lp-mark"), Span("{name}"), href="/", cls="lp-brand"),
                Div(A("Partners", href="#partners", cls="lp-nav-link"),
                    A("Developers", href="/developers", cls="lp-nav-link"),
                    Button("Sign In", type="button", onclick="authOpen('login')", cls="lp-signin"),
                    cls="lp-nav-actions"), cls="lp-nav"),
            Main(
                Section(Span("{eyebrow}", cls="lp-kicker"), H1("{headline}"),
                        P("{description}", cls="lp-lede"),
                        Div(Button("Sign In or Register", type="button", onclick="authOpen('login')", cls="lp-primary"),
                            A("Explore the open-source suite →", href="https://fastsme.com/products", cls="lp-secondary"),
                            cls="lp-actions"), cls="lp-hero"),
                Section(Div(Img(src="{demo_url}", alt="{name} product tour",
                                loading="eager", width="1854", height="909"),
                            P("Product tour · see the workspace in action"),
                            cls="lp-demo-frame"), cls="lp-demo", aria_label="{name} product tour"),
                Section(Div(*[Article(Span(f"0{{i}}", cls="lp-num"), H2(title),
                                      P("Everything you need for " + title.lower() + ", in one focused workspace."),
                                      cls="lp-card") for i, title in enumerate(features, 1)],
                            cls="lp-grid"), cls="lp-band"),
                partner_section(),
                Section(Div(Span("Developers", cls="lp-kicker"),
                            H2("Build on {name}."),
                            P("Explore the public read API, typed schemas, examples, and token-gated integration writes.")),
                        A("Read the API documentation →", href="/developers", cls="lp-primary"),
                        cls="lp-developers"),
            ),
            Footer(Span("{name} is part of the open-source FastSME suite."),
                   A("View all products", href="https://fastsme.com/products", style="color:var(--accent)"),
                   cls="lp-footer"),
            auth_modal("{name}"),
            Script(AUTH_JS),
        ),
    )
'''

DEVELOPER_TEMPLATE = '''"""Public and in-app developer documentation for {name}."""
from fasthtml.common import *

from .{api_module} import RESOURCES
from .landing import FAVICON
from .seo import seo_meta

ACCENT = "{accent}"
TINT = "{tint}"
BASE_URL = "{base_url}"
REPOSITORY = "https://github.com/predictivelabsai/{name}"

DEVELOPER_CSS = """
.dev-docs{{--dev-accent:{accent};--dev-tint:{tint};--dev-ink:#111827;--dev-muted:#667085;--dev-line:#e7eaf0;color:var(--dev-ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}}
.dev-docs *{{box-sizing:border-box}} .dev-wrap{{max-width:1120px;margin:auto;padding:56px 24px 80px}}
.dev-eyebrow{{color:var(--dev-accent);font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.16em}}
.dev-docs h1{{font-size:clamp(40px,6vw,68px);line-height:1.02;letter-spacing:-.05em;max-width:850px;margin:18px 0}}
.dev-lede{{font-size:19px;line-height:1.65;color:var(--dev-muted);max-width:760px}}
.dev-actions{{display:flex;gap:10px;flex-wrap:wrap;margin:28px 0 46px}} .dev-btn{{display:inline-flex;padding:10px 16px;border-radius:999px;text-decoration:none;font-size:14px;font-weight:700;border:1px solid var(--dev-line);color:var(--dev-ink);background:white}} .dev-btn.primary{{background:var(--dev-accent);color:white;border-color:var(--dev-accent)}}
.dev-note{{background:var(--dev-tint);border:1px solid color-mix(in srgb,var(--dev-accent) 18%,white);border-radius:18px;padding:20px 22px;line-height:1.6;margin-bottom:42px}} .dev-note strong{{color:var(--dev-accent)}}
.dev-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:18px 0 46px}} .dev-card{{background:white;border:1px solid var(--dev-line);border-radius:18px;padding:22px;box-shadow:0 8px 24px rgba(17,24,39,.04)}} .dev-card h2{{font-size:19px;margin:0 0 8px}} .dev-card p{{color:var(--dev-muted);line-height:1.55;min-height:48px}} .dev-route{{display:block;background:#111827;color:#f8fafc;padding:9px 11px;border-radius:8px;margin-top:8px;font:12px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;overflow:auto}} .dev-method{{color:#86efac;font-weight:800}}
.dev-example{{background:#111827;color:#e5e7eb;border-radius:16px;padding:22px;overflow:auto;font:13px/1.65 ui-monospace,SFMono-Regular,Menlo,monospace}} .dev-docs h3{{font-size:24px;margin:42px 0 14px}} .dev-small{{color:var(--dev-muted);font-size:13px;line-height:1.6}}
.dev-public-nav{{height:68px;display:flex;align-items:center;justify-content:space-between;max-width:1120px;margin:auto;padding:0 24px;border-bottom:1px solid var(--dev-line)}} .dev-brand{{display:flex;align-items:center;gap:10px;color:var(--dev-ink);text-decoration:none;font-weight:750}} .dev-diamond{{width:28px;height:28px;border-radius:8px;background:var(--dev-accent);transform:rotate(45deg);display:inline-block}}
@media(max-width:720px){{.dev-grid{{grid-template-columns:1fr}}.dev-docs h1{{font-size:42px}}}}
"""


def developer_content():
    cards = []
    for resource in RESOURCES:
        cards.append(
            Article(
                H2(resource.title),
                P(resource.description),
                Code(Span("GET", cls="dev-method"), f" /api/v1/{{resource.slug}}", cls="dev-route"),
                Code(Span("GET", cls="dev-method"), f" /api/v1/{{resource.slug}}/{{{{id}}}}", cls="dev-route"),
                cls="dev-card",
            )
        )
    return Div(
        Style(DEVELOPER_CSS),
        Div(
            Span("Developer platform · API v1", cls="dev-eyebrow"),
            H1("Build with the {name} API."),
            P("Read the live demo database through a typed, versioned API. Selected integration writes are implemented behind bearer-token authentication.", cls="dev-lede"),
            Div(
                A("Open Swagger UI", href="/api/docs", cls="dev-btn primary"),
                A("Open ReDoc", href="/api/redoc", cls="dev-btn"),
                A("Download swagger.json", href="/swagger.json", cls="dev-btn"),
                A("View on GitHub", href=REPOSITORY, target="_blank", rel="noreferrer", cls="dev-btn"),
                cls="dev-actions",
            ),
            Div(
                Strong("Public preview access. "),
                "GET endpoints require no authentication. Writes return 503 until FASTSME_API_TOKEN is configured; enabled clients send Authorization: Bearer <token>.",
                cls="dev-note",
            ),
            H3("Resources"),
            Div(*cards, cls="dev-grid"),
            H3("Quick start"),
            Pre(Code(f"""curl "{{BASE_URL}}/api/v1/{{RESOURCES[0].slug}}?limit=20"\n\npython - <<'PY'\nimport requests\nrows = requests.get("{{BASE_URL}}/api/v1/{{RESOURCES[0].slug}}", timeout=20).json()\nprint(rows["data"])\nPY"""), cls="dev-example"),
            P("Runtime OpenAPI: /api/openapi.json · Stable compatibility schema: /swagger.json · Interactive docs: /api/docs", cls="dev-small"),
            cls="dev-wrap",
        ),
        cls="dev-docs",
    )


def developer_page():
    return Html(
        Head(
            Title("{name} Developers · FastSME"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="description", content="Developer API documentation for {name}."),
            *seo_meta(
                path="/developers",
                title="{name} Developer API · FastSME",
                description="Build integrations with the public {name} API, OpenAPI schemas, examples, and token-gated writes.",
            ),
            Link(rel="icon", type="image/svg+xml", href=FAVICON),
            Link(rel="preconnect", href="https://fonts.googleapis.com"),
            Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;750&display=swap"),
        ),
        Body(
            Nav(
                A(Span(cls="dev-diamond"), Span("{name} Developers"), href="/developers", cls="dev-brand"),
                A("Back to product", href="/", cls="dev-btn"),
                cls="dev-public-nav dev-docs",
            ),
            developer_content(),
            style="margin:0;background:#fff",
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


def render_seo_module(name: str, meta: dict) -> str:
    """Render indexable metadata and crawler routes from portfolio truth."""
    description = meta["description"]
    eyebrow = meta["eyebrow"].lower()
    keywords = tuple(dict.fromkeys((
        name,
        f"open source {eyebrow}",
        f"{eyebrow} software",
        f"SME {eyebrow}",
        *meta["features"],
        "FastSME",
        "open source business software",
    )))
    base_url = meta.get("domain", f"https://{meta['slug']}.fastsme.com")
    sitemap_paths = tuple(meta.get("sitemap_paths", ("/", "/developers")))
    return f'''"""Search metadata, structured data, sitemap, and crawler policy."""
from __future__ import annotations

import json

from fasthtml.common import Link, Meta, NotStr, Script
from starlette.responses import Response

PRODUCT = {name!r}
BASE_URL = {base_url!r}
DESCRIPTION = {description!r}
KEYWORDS = {keywords!r}
FEATURES = {tuple(meta["features"])!r}
SITEMAP_PATHS = {sitemap_paths!r}


def seo_meta(
    *,
    path: str = "/",
    title: str | None = None,
    description: str | None = None,
):
    canonical = BASE_URL + (path if path != "/" else "")
    page_title = title or f"{{PRODUCT}} · Open-source {{KEYWORDS[2].title()}}"
    page_description = description or DESCRIPTION
    structured = {{
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": PRODUCT,
        "url": canonical,
        "description": page_description,
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "isAccessibleForFree": True,
        "license": "https://opensource.org/license/mit",
        "featureList": list(FEATURES),
        "publisher": {{
            "@type": "Organization",
            "name": "FastSME",
            "url": "https://fastsme.com",
        }},
    }}
    return (
        Link(rel="canonical", href=canonical),
        Meta(name="robots", content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"),
        Meta(name="keywords", content=", ".join(KEYWORDS)),
        Meta(property="og:type", content="website"),
        Meta(property="og:site_name", content="FastSME"),
        Meta(property="og:title", content=page_title),
        Meta(property="og:description", content=page_description),
        Meta(property="og:url", content=canonical),
        Meta(name="twitter:card", content="summary"),
        Meta(name="twitter:title", content=page_title),
        Meta(name="twitter:description", content=page_description),
        Script(NotStr(json.dumps(structured, separators=(",", ":"))), type="application/ld+json"),
    )


async def sitemap():
    urls = "\\n".join(
        f'  <url><loc>{{BASE_URL}}{{path}}</loc><changefreq>{{"weekly" if path == "/" else "monthly"}}</changefreq><priority>{{"1.0" if path == "/" else "0.6"}}</priority></url>'
        for path in SITEMAP_PATHS
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{{urls}}
</urlset>
"""
    return Response(xml, media_type="application/xml")


async def robots():
    body = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /app
Disallow: /auth/
Disallow: /login
Disallow: /register
Disallow: /api/

Sitemap: {{BASE_URL}}/sitemap.xml
"""
    return Response(body, media_type="text/plain")


def register_seo_routes(app):
    paths = {{getattr(route, "path", None) for route in app.routes}}
    if "/sitemap.xml" not in paths:
        app.route("/sitemap.xml", methods=["GET"])(sitemap)
        app.routes.insert(0, app.routes.pop())
    if "/robots.txt" not in paths:
        app.route("/robots.txt", methods=["GET"])(robots)
        app.routes.insert(0, app.routes.pop())
'''


SEO_TARGETS = {
    "FastBooking": (
        "app/ui/seo.py",
        "app/ui/main.py",
        "app.ui.seo",
        "    # register page routes",
    ),
    "FastFunnel": ("fastfunnel/web/seo.py", "fastfunnel/app.py", "fastfunnel.web.seo", "\ndef main():"),
    "FastCMS": ("app/seo.py", "main.py", "app.seo", "\nserve()"),
    "FastFund": ("web/seo.py", "web/app.py", "web.seo", None),
    "FastLMS": ("components/seo.py", "main.py", "components.seo", '\nif __name__ == "__main__":'),
    "FastPPM": ("web/seo.py", "web/app.py", "web.seo", None),
    "FastWiki": ("fastwiki/seo.py", "app.py", "fastwiki.seo", None),
    "FastCal": ("seo.py", "app.py", "seo", None),
    "FastOffice": ("seo.py", "app.py", "seo", None),
}


def sync_seo(name: str, meta: dict, check: bool) -> list[str]:
    """Synchronise the SEO module and its application route registration."""
    repo = FASTCO / name
    seo_rel, app_rel, module, marker = SEO_TARGETS.get(
        name, ("web/seo.py", "web_app.py", "web.seo", '\nif __name__ == "__main__":')
    )
    seo_path = repo / seo_rel
    expected = (
        seo_path.read_text()
        if name == "FastBooking" and seo_path.exists()
        else render_seo_module(name, meta)
    )
    changes = []
    if not seo_path.exists() or seo_path.read_text() != expected:
        changes.append(seo_rel)
        if not check:
            seo_path.parent.mkdir(parents=True, exist_ok=True)
            seo_path.write_text(expected)

    app_path = repo / app_rel
    source = app_path.read_text()
    updated = source
    import_line = f"from {module} import register_seo_routes"
    if import_line not in updated:
        lines = updated.splitlines(keepends=True)
        insertion = next(
            (index + 1 for index, line in enumerate(lines) if "landing import" in line),
            next((index + 1 for index, line in enumerate(lines) if line.startswith("from fasthtml.common import")), 1),
        )
        lines.insert(insertion, import_line + "\n")
        updated = "".join(lines)
    registration = (
        "    register_seo_routes(app)"
        if name == "FastBooking"
        else "register_seo_routes(app)"
    )
    if registration not in updated:
        block = f"\n\n{registration}\n"
        if marker and marker in updated:
            updated = updated.replace(marker, block + marker, 1)
        else:
            updated = updated.rstrip() + block
    if updated != source:
        changes.append(app_rel)
        if not check:
            app_path.write_text(updated)
    return changes

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
    meta = {"demo_url": "/static/product-demo.gif", **meta}
    meta["base_url"] = meta.get("domain", f"https://{meta['slug']}.fastsme.com")
    if meta.get("cohort") == "streamlit":
        return []
    custom_paths = {
        "FastFunnel": "fastfunnel/web/landing.py",
        "FastCMS": "app/landing.py",
        "FastFund": "web/landing.py",
        "FastLMS": "components/landing.py",
        "FastPPM": "web/landing.py",
    }
    seo_changes = sync_seo(name, meta, check)
    # Some products provide intentionally bespoke landing pages. They still
    # belong in the portfolio catalogue. Their SEO routes are synchronised,
    # while their intentionally bespoke landing markup remains hand-maintained.
    if meta.get("cohort") == "custom" and name not in custom_paths:
        return seo_changes
    demo_source = repo / meta["demo_gif"]
    demo_target = repo / "static/product-demo.gif"
    asset_changes = seo_changes
    if not demo_source.is_file():
        raise SystemExit(f"{name}: missing demo GIF: {demo_source.relative_to(repo)}")
    if not demo_target.is_file() or demo_target.read_bytes() != demo_source.read_bytes():
        asset_changes.append(str(demo_target.relative_to(repo)))
        if not check:
            demo_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(demo_source, demo_target)
    if meta.get("cohort") == "custom":
        path = repo / custom_paths[name]
        expected = LANDING_TEMPLATE.format(name=name, **meta)
        expected_developer = DEVELOPER_TEMPLATE.format(
            name=name,
            api_module="fastapi_api" if name == "FastCMS" else "api",
            **meta,
        )
        developer_path = path.with_name("developer.py")
        oauth_path = path.with_name("google_auth.py")
        account_path = path.with_name("account_auth.py")
        changed = asset_changes
        if not path.exists() or path.read_text() != expected:
            if not check:
                path.write_text(expected)
            changed.append(str(path.relative_to(repo)))
        if not developer_path.exists() or developer_path.read_text() != expected_developer:
            if not check:
                developer_path.write_text(expected_developer)
            changed.append(str(developer_path.relative_to(repo)))
        if name in {"FastCMS", "FastLMS"} and (
                not oauth_path.exists() or oauth_path.read_text() != OAUTH_MODULE):
            if not check:
                oauth_path.write_text(OAUTH_MODULE)
            changed.append(str(oauth_path.relative_to(repo)))
        expected_account = (SKILL_ROOT / "templates/account_auth.py").read_text()
        if name != "FastFunnel" and (
                not account_path.exists() or account_path.read_text() != expected_account):
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
                f"FASTSME_PUBLIC_URL={meta['base_url']}\n"
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
    expected_developer = DEVELOPER_TEMPLATE.format(
        name=name,
        api_module="api",
        **meta,
    )
    developer_path = repo / "web/developer.py"
    expected_account = (SKILL_ROOT / "templates/account_auth.py").read_text()
    for path, expected in ((landing_path, expected_landing), (developer_path, expected_developer),
                           (oauth_path, OAUTH_MODULE),
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
                f"GOOGLE_REDIRECT_URI={meta['base_url']}/auth/google/callback\n"
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
                f"FASTSME_PUBLIC_URL={meta['base_url']}\n"
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
