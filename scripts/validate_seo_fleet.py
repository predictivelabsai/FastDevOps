#!/usr/bin/env python3
"""Validate the generated FastSME SEO contract without importing product apps."""

from __future__ import annotations

import py_compile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FASTCO = ROOT.parent
PORTFOLIO = ROOT / "skills/fastsme-landing/references/portfolio.yaml"

SPECIAL = {
    "FastBooking": (
        "app/ui/seo.py",
        "app/ui/pages/platform.py",
        "app/ui/main.py",
    ),
    "FastWiki": ("fastwiki/seo.py", "fastwiki/views.py", "app.py"),
    "FastCal": ("seo.py", "views.py", "app.py"),
    "FastOffice": ("seo.py", "views.py", "app.py"),
    "FastFunnel": ("fastfunnel/web/seo.py", "fastfunnel/web/landing.py", "fastfunnel/app.py"),
    "FastCMS": ("app/seo.py", "app/landing.py", "main.py"),
    "FastFund": ("web/seo.py", "web/landing.py", "web/app.py"),
    "FastLMS": ("components/seo.py", "components/landing.py", "main.py"),
    "FastPPM": ("web/seo.py", "web/landing.py", "web/app.py"),
}


def main() -> None:
    apps = yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))["apps"]
    errors: list[str] = []
    checked = 0
    for name, meta in apps.items():
        if meta.get("cohort") == "streamlit":
            continue
        checked += 1
        seo_rel, landing_rel, app_rel = SPECIAL.get(
            name, ("web/seo.py", "web/landing.py", "web_app.py")
        )
        repo = FASTCO / name
        seo_path = repo / seo_rel
        landing_path = repo / landing_rel
        app_path = repo / app_rel
        for path in (seo_path, landing_path, app_path):
            if not path.is_file():
                errors.append(f"{name}: missing {path.relative_to(repo)}")
        if not seo_path.is_file() or not landing_path.is_file() or not app_path.is_file():
            continue
        seo = seo_path.read_text(encoding="utf-8")
        landing = landing_path.read_text(encoding="utf-8")
        app = app_path.read_text(encoding="utf-8")
        expected_url = meta.get("domain", f"https://{meta['slug']}.fastsme.com")
        checks = {
            "canonical base URL": expected_url in seo,
            "sitemap route": '"/sitemap.xml"' in seo,
            "robots route": '"/robots.txt"' in seo,
            "structured data": '"@type": "SoftwareApplication"' in seo,
            "Open Graph metadata": 'property="og:title"' in seo,
            "Twitter metadata": 'name="twitter:card"' in seo,
            "crawler registration": "register_seo_routes(app)" in app,
            "landing metadata": "seo_meta" in landing,
        }
        errors.extend(
            f"{name}: missing {label}" for label, valid in checks.items() if not valid
        )
        try:
            py_compile.compile(str(seo_path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"{name}: SEO module does not compile ({exc.msg})")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"valid: {checked} FastSME SEO product(s)")


if __name__ == "__main__":
    main()
