"""Small, secret-safe Coolify v4 API client."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class Coolify:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token = os.getenv("COOLIFY_API_TOKEN")
        if not self.token:
            raise RuntimeError("COOLIFY_API_TOKEN is not set")

    def request(self, method: str, path: str, body: dict | None = None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            f"{self.base_url}/api/v1{path}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            # Do not include response bodies: they may echo secret input.
            raise RuntimeError(
                f"Coolify API {method} {path} returned HTTP {exc.code}"
            ) from exc

    def applications(self) -> list[dict]:
        return self.request("GET", "/applications") or []

    def find_application(self, name: str) -> dict | None:
        return next((app for app in self.applications() if app.get("name") == name), None)

    def application(self, uuid: str) -> dict:
        return self.request("GET", f"/applications/{uuid}") or {}

    def create_public_application(self, body: dict) -> dict:
        return self.request("POST", "/applications/public", body) or {}

    def update_application(self, uuid: str, body: dict) -> dict:
        return self.request("PATCH", f"/applications/{uuid}", body) or {}

    def storages(self, uuid: str) -> list[dict]:
        result = self.request("GET", f"/applications/{uuid}/storages") or {}
        return result.get("persistent_storages", [])

    def create_storage(self, uuid: str, name: str, mount_path: str) -> dict:
        return self.request(
            "POST",
            f"/applications/{uuid}/storages",
            {"type": "persistent", "name": name, "mount_path": mount_path},
        ) or {}

    def environment_names(self, uuid: str) -> list[str]:
        rows = self.request("GET", f"/applications/{uuid}/envs") or []
        return sorted(row.get("key", "") for row in rows if row.get("key"))

    def sync_environment(self, uuid: str, variables: dict[str, str]) -> None:
        if not variables:
            return
        data = [
            {
                "key": key,
                "value": str(value),
                "is_preview": False,
                "is_literal": True,
                "is_multiline": False,
            }
            for key, value in variables.items()
        ]
        self.request("PATCH", f"/applications/{uuid}/envs/bulk", {"data": data})

    def deploy(self, uuid: str) -> dict:
        result = self.request("POST", "/deploy", {"uuid": uuid}) or {}
        deployments = result.get("deployments", [])
        return deployments[0] if deployments else result
