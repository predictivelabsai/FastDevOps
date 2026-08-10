#!/usr/bin/env python3
"""Audit gcloud context and a web app's Google OAuth callback without exposing secrets."""

from __future__ import annotations

import argparse
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def gcloud_value(*args: str) -> str:
    result = subprocess.run(
        ["gcloud", *args], text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gcloud command failed")
    return result.stdout.strip()


def probe_authorization(client_id: str, redirect_uri: str) -> tuple[bool, bool]:
    query = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": "callback-audit-only",
        }
    )
    request = urllib.request.Request(
        "https://accounts.google.com/o/oauth2/v2/auth?" + query,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
    mismatch = "redirect_uri_mismatch" in body
    authorization_page = "accounts.google.com" in body or "Sign in with Google" in body
    return mismatch, authorization_page


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--project", help="expected configured gcloud project")
    parser.add_argument("--skip-network", action="store_true")
    args = parser.parse_args()

    env = read_env(args.env_file)
    required = ("GOOGLE_CLIENT_ID", "GOOGLE_REDIRECT_URI")
    missing = [key for key in required if not env.get(key)]
    if missing:
        raise ValueError("env file is missing: " + ", ".join(missing))

    active_account = gcloud_value(
        "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"
    )
    configured_project = gcloud_value("config", "get-value", "project")
    if not active_account:
        raise RuntimeError("gcloud has no active account")
    if args.project and configured_project != args.project:
        raise RuntimeError(
            f"configured gcloud project is {configured_project!r}, expected {args.project!r}"
        )

    print(f"active_account={active_account}")
    print(f"configured_project={configured_project}")
    print(f"redirect_uri={env['GOOGLE_REDIRECT_URI']}")
    print(
        "oauth_clients_url="
        f"https://console.cloud.google.com/auth/clients?project={configured_project}"
    )
    print("client_id_present=true")

    if args.skip_network:
        print("authorization_probe=skipped")
        return 0

    mismatch, authorization_page = probe_authorization(
        env["GOOGLE_CLIENT_ID"], env["GOOGLE_REDIRECT_URI"]
    )
    print(f"redirect_uri_mismatch={str(mismatch).lower()}")
    print(f"google_authorization_page={str(authorization_page).lower()}")
    return 1 if mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
