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


def load_local_env(path: Path) -> dict[str, str]:
    values = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def load_control_plane_env() -> None:
    for key, value in load_local_env(ROOT / ".env").items():
        os.environ.setdefault(key, value)


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
    base_url = os.getenv("COOLIFY_BASE_URL", env["coolify"]["base_url"])
    return Coolify(base_url)


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


def provision_body(name: str, service: dict, env: dict) -> dict:
    build = service["build"]
    body = {
        "project_uuid": env["coolify"]["project_uuid"],
        "environment_uuid": env["coolify"]["environment_uuid"],
        "server_uuid": env["coolify"]["server_uuid"],
        "git_repository": f"https://github.com/{service['repo']}",
        "git_branch": service["branch"],
        "build_pack": build["type"],
        "ports_exposes": str(service["port"]),
        "name": name,
        "domains": service["domain"],
        "is_auto_deploy_enabled": True,
        "is_force_https_enabled": True,
        "autogenerate_domain": False,
        "instant_deploy": False,
    }
    if build["type"] == "dockerfile":
        body["dockerfile_location"] = build["dockerfile"]
    if build.get("start_command"):
        body["start_command"] = build["start_command"]
    return body


def application_settings(name: str, service: dict) -> dict:
    settings = {
        "description": service.get("description", f"{name} FastSME service"),
        "health_check_enabled": False,
        "limits_memory": service.get("limits_memory", "768M"),
        "limits_cpus": service.get("limits_cpus", "1"),
    }
    settings["custom_docker_run_options"] = ""
    return settings


def cmd_provision(args):
    if not args.yes:
        target = args.service or "the complete fleet"
        if input(f"Create or reconcile {target} in Coolify? [y/N] ").strip().lower() != "y":
            print("aborted")
            return
    api = client(args.env)
    env = environment(args.env)
    existing = {app.get("name"): app for app in api.applications()}
    for name, service in select(args.service):
        body = provision_body(name, service, env)
        app = existing.get(name)
        if app:
            if name == "fastfunnel":
                print(f"{name}: exists {app['uuid']} (unchanged)")
            else:
                api.update_application(
                    app["uuid"], application_settings(name, service)
                )
                if service.get("volume") and not any(
                    row.get("mount_path") == service["volume"]
                    for row in api.storages(app["uuid"])
                ):
                    api.create_storage(app["uuid"], "data", service["volume"])
                print(f"{name}: reconciled {app['uuid']}")
        else:
            result = api.create_public_application(body)
            uuid = result.get("uuid")
            if not uuid:
                raise RuntimeError(f"{name}: Coolify did not return an application UUID")
            api.update_application(uuid, application_settings(name, service))
            if service.get("volume"):
                api.create_storage(uuid, "data", service["volume"])
            print(f"{name}: created {uuid}")


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
    for name, service in select(args.service):
        app = require_app(api, name)
        if args.sync:
            if not args.yes:
                answer = input(f"Sync declared runtime variables to {name}? [y/N] ")
                if answer.strip().lower() != "y":
                    print("aborted")
                    continue
            local_dir = ROOT.parent / service.get("local_dir", name)
            source = load_local_env(local_dir / ".env")
            shared = load_local_env(ROOT.parent / "FastFunnel" / ".env")
            env_config = service.get("env", {})
            variables = {
                key: source.get(key) or shared[key]
                for key in env_config.get("required", [])
                if source.get(key) or shared.get(key)
            }
            missing = [
                key for key in env_config.get("required", [])
                if key not in variables
            ]
            if missing:
                raise RuntimeError(
                    f"{name}: required variables missing from {local_dir / '.env'}: "
                    + ", ".join(missing)
                )
            variables.update({
                key: str(value)
                for key, value in env_config.get("runtime", {}).items()
            })
            api.sync_environment(app["uuid"], variables)
            print(f"{name}: synchronized {len(variables)} variable(s); values hidden")
            continue
        names = api.environment_names(app["uuid"])
        print(f"{name}: {', '.join(names) if names else '(none)'}")


def cmd_deploy(args):
    if not args.yes:
        answer = input(f"Deploy {args.service or 'the complete fleet'}? [y/N] ")
        if answer.strip().lower() != "y":
            print("aborted")
            return
    api = client(args.env)
    for name, _service in select(args.service):
        app = require_app(api, name)
        result = api.deploy(app["uuid"])
        deployment = result.get("deployment_uuid", "queued")
        print(f"{name}: deployment {deployment}")


def main():
    load_control_plane_env()
    parser = argparse.ArgumentParser(description="FastSME Coolify/Pulumi orchestrator")
    parser.add_argument("--env", default="production")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.set_defaults(func=cmd_validate)
    doctor = sub.add_parser("doctor")
    doctor.add_argument("service", nargs="?")
    doctor.set_defaults(func=cmd_doctor)
    provision = sub.add_parser("provision")
    provision.add_argument("service", nargs="?")
    provision.add_argument("--yes", action="store_true")
    provision.set_defaults(func=cmd_provision)
    status = sub.add_parser("status")
    status.add_argument("service", nargs="?")
    status.set_defaults(func=cmd_status)
    env = sub.add_parser("env", help="list variable names; values are never printed")
    env.add_argument("service", nargs="?")
    env.add_argument("--sync", action="store_true", help="sync declared values from sibling .env")
    env.add_argument("--yes", action="store_true", help="skip mutation confirmation")
    env.set_defaults(func=cmd_env)
    deploy = sub.add_parser("deploy")
    deploy.add_argument("service", nargs="?")
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
