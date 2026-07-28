#!/usr/bin/env python3
"""FastDevOps control-plane CLI."""

from __future__ import annotations

import argparse
import os
import ssl
import sys
import urllib.request
from pathlib import Path

import yaml

from providers.coolify import Coolify

ROOT = Path(__file__).resolve().parent


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def catalog() -> dict:
    raw = load_yaml(ROOT / "config/services.yaml")
    defaults = raw.get("defaults", {})
    services = {}
    for name, service in raw.get("services", {}).items():
        merged = defaults | service
        merged["build"] = defaults.get("build", {}) | service.get("build", {})
        merged["cloud_run"] = defaults.get("cloud_run", {}) | service.get("cloud_run", {})
        services[name] = merged
    return services


def environment(name: str) -> dict:
    return load_yaml(ROOT / f"config/environments/{name}.yaml")


def select(name: str | None) -> list[tuple[str, dict]]:
    services = catalog()
    if name:
        if name not in services:
            raise RuntimeError(f"unknown service {name!r}; choose: {', '.join(services)}")
        return [(name, services[name])]
    return list(services.items())


def client(env_name: str) -> Coolify:
    env = environment(env_name)
    if env.get("provider") != "coolify":
        raise RuntimeError(f"environment {env_name!r} is not a Coolify environment")
    return Coolify(env["coolify"]["base_url"])


def health(url: str, path: str) -> str:
    try:
        with urllib.request.urlopen(url.rstrip("/") + path, timeout=10) as response:
            return f"HTTP {response.status}"
    except Exception as exc:
        return f"unreachable ({type(exc).__name__})"


def cmd_validate(_args):
    errors = []
    for name, service in select(None):
        for field in ("repo", "port", "domain", "health"):
            if not service.get(field):
                errors.append(f"{name}: missing {field}")
        if not str(service.get("domain", "")).endswith(".fastsme.com"):
            errors.append(f"{name}: domain must be under fastsme.com")
    if errors:
        raise RuntimeError("; ".join(errors))
    print(f"valid: {len(catalog())} service(s)")


def cmd_doctor(args):
    cmd_validate(args)
    env = environment(args.env)
    base_url = env["coolify"]["base_url"]
    try:
        ssl.create_default_context()
        with urllib.request.urlopen(f"{base_url}/api/health", timeout=10) as response:
            print(f"coolify: HTTP {response.status}")
    except Exception as exc:
        print(f"coolify: unreachable or TLS invalid ({type(exc).__name__})")
    print(f"token: {'present' if os.getenv('COOLIFY_API_TOKEN') else 'missing'}")
    for name, service in select(args.service):
        local = ROOT.parent / service.get("local_dir", name)
        print(f"{name}: repo={'present' if local.is_dir() else 'missing'} domain={service['domain']}")


def require_app(api: Coolify, name: str) -> dict:
    app = api.find_application(name)
    if not app:
        raise RuntimeError(f"Coolify application {name!r} was not found; create it in the dashboard")
    return app


def cmd_status(args):
    api = client(args.env)
    for name, service in select(args.service):
        app = require_app(api, name)
        detail = api.application(app["uuid"])
        print(
            f"{name}: status={detail.get('status', 'unknown')} "
            f"url={detail.get('fqdn') or service['domain']} "
            f"health={health(service['domain'], service['health']['path'])}"
        )


def cmd_env(args):
    api = client(args.env)
    for name, _service in select(args.service):
        app = require_app(api, name)
        names = api.environment_names(app["uuid"])
        print(f"{name}: {', '.join(names) if names else '(none)'}")


def cmd_deploy(args):
    if not args.yes:
        answer = input(f"Deploy {args.service} from its configured branch? [y/N] ")
        if answer.strip().lower() != "y":
            print("aborted")
            return
    api = client(args.env)
    app = require_app(api, args.service)
    result = api.deploy(app["uuid"])
    deployment = result.get("deployment_uuid", "queued")
    print(f"{args.service}: deployment {deployment}")


def main():
    parser = argparse.ArgumentParser(description="FastSME Coolify/Pulumi orchestrator")
    parser.add_argument("--env", default="production")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.set_defaults(func=cmd_validate)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("service", nargs="?")
    doctor.set_defaults(func=cmd_doctor)
    status = sub.add_parser("status")
    status.add_argument("service", nargs="?")
    status.set_defaults(func=cmd_status)
    env = sub.add_parser("env", help="list variable names; values are never printed")
    env.add_argument("service", nargs="?")
    env.set_defaults(func=cmd_env)
    deploy = sub.add_parser("deploy")
    deploy.add_argument("service")
    deploy.add_argument("--yes", action="store_true")
    deploy.set_defaults(func=cmd_deploy)
    args = parser.parse_args()
    try:
        args.func(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
