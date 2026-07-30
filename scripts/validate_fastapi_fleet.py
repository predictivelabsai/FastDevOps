#!/usr/bin/env python3
"""Validate committed API surfaces across the migrated FastSME products."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FASTCO = ROOT.parent
PORTFOLIO = ROOT / "skills/fastsme-landing/references/portfolio.yaml"
API_DEFERRED = {"FastWiki", "FastOffice"}


def main() -> int:
    apps = yaml.safe_load(PORTFOLIO.read_text())["apps"]
    failures: list[str] = []
    checked = 0
    custom_dirs = {
        "FastCal": ".",
        "FastFunnel": "fastfunnel/web",
        "FastCMS": "app",
        "FastFund": "web",
        "FastLMS": "components",
        "FastPPM": "web",
    }
    entrypoints = {
        "FastCal": "app.py",
        "FastFunnel": "fastfunnel/app.py",
        "FastCMS": "main.py",
        "FastFund": "web/app.py",
        "FastLMS": "main.py",
        "FastPPM": "web/app.py",
    }
    for name, metadata in apps.items():
        if metadata.get("cohort") == "streamlit" or name in API_DEFERRED:
            continue
        checked += 1
        repo = FASTCO / name
        if name == "FastBooking":
            required = (
                repo / "app/api/main.py",
                repo / "app/api/routers/platform.py",
                repo / "app/ui/pages/platform.py",
                repo / "app/main_monolith.py",
            )
            for path in required:
                if not path.is_file():
                    failures.append(f"{name}: missing {path.relative_to(repo)}")
            if any(not path.is_file() for path in required):
                continue
            api_source = required[0].read_text()
            routes = required[1].read_text()
            landing = required[2].read_text()
            entrypoint_source = required[3].read_text()
            checks = (
                ("FastBooking API", "branded API title", api_source),
                ("/public/{tenant_slug}/catalogue", "tenant catalogue", routes),
                ("/bookings/restaurant", "restaurant booking write", routes),
                ("/bookings/hotel", "hotel booking write", routes),
                ("/bookings/clinic", "clinic booking write", routes),
                ("/bookings/events", "event booking write", routes),
                ('href="/developers"', "landing Developers link", landing),
                ('href="/api/docs"', "Swagger link", landing),
                ('href="/swagger.json"', "schema link", landing),
                ('Mount("/api"', "mounted FastAPI application", entrypoint_source),
            )
            failures.extend(
                f"{name}: missing {label}"
                for needle, label, text in checks
                if needle not in text
            )
            continue
        module_dir = repo / custom_dirs.get(name, "web")
        entrypoint = repo / entrypoints.get(name, "web_app.py")
        required = (
            module_dir / "api_core.py",
            module_dir / ("fastapi_api.py" if name == "FastCMS" else "api.py"),
            module_dir / "developer.py",
            repo / "swagger.json",
            entrypoint,
        )
        for path in required:
            if not path.is_file():
                failures.append(f"{name}: missing {path.relative_to(repo)}")
        if any(not path.is_file() for path in required):
            continue

        try:
            schema = json.loads((repo / "swagger.json").read_text())
        except (json.JSONDecodeError, OSError) as exc:
            failures.append(f"{name}: invalid swagger.json: {exc}")
            continue
        if not str(schema.get("openapi", "")).startswith("3."):
            failures.append(f"{name}: swagger.json is not OpenAPI 3")
        paths = schema.get("paths", {})
        if "/v1/health" not in paths:
            failures.append(f"{name}: missing /v1/health")
        reads = [
            path for path, operations in paths.items()
            if path.startswith("/v1/") and path != "/v1/health"
            and "{" not in path and "get" in operations
        ]
        if len(reads) < 2:
            failures.append(f"{name}: expected at least two resource collections")
        if not any("post" in operations for operations in paths.values()):
            failures.append(f"{name}: no selected write operation")

        landing = (repo / "views.py").read_text() if name == "FastCal" else (module_dir / "landing.py").read_text()
        developer = (module_dir / "developer.py").read_text()
        source = entrypoint.read_text()
        for needle, label, text in (
            ('href="/developers"', "landing Developers link", landing),
            ('href="/api/docs"', "Swagger link", developer),
            ('href="/swagger.json"', "schema link", developer),
            ("mount(", "mounted FastAPI application", source),
            ("/swagger.json", "runtime compatibility schema", source),
            ("/developers", "developer route", source),
        ):
            if needle not in text:
                failures.append(f"{name}: missing {label}")
        if not any(
            token in developer
            for token in ("FASTSME_API_TOKEN", "FASTFUNNEL_WORKSPACE_TOKEN")
        ):
            failures.append(f"{name}: missing write-auth explanation")

    if failures:
        print("FastSME API validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"valid: {checked} FastSME API product(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
