"""GCP Cloud Run resources generated from the FastDevOps service catalog."""

from pathlib import Path

import pulumi
import pulumi_gcp as gcp
import yaml

root = Path(__file__).resolve().parents[2]
raw = yaml.safe_load((root / "config/services.yaml").read_text())
defaults = raw.get("defaults", {})
services = raw["services"]
config = pulumi.Config()
gcp_config = pulumi.Config("gcp")
project = gcp_config.require("project")
region = gcp_config.get("region") or "europe-west1"
registry_name = config.get("registry") or "fastsme"

registry = gcp.artifactregistry.Repository(
    "fastsme-registry",
    repository_id=registry_name,
    location=region,
    format="DOCKER",
)

for name, specific in services.items():
    service = defaults | specific
    run = defaults.get("cloud_run", {}) | specific.get("cloud_run", {})
    image = f"{region}-docker.pkg.dev/{project}/{registry_name}/{name}:latest"
    cloud_run = gcp.cloudrunv2.Service(
        name,
        name=name,
        location=region,
        template={
            "containers": [{
                "image": image,
                "ports": [{"container_port": service["port"]}],
                "resources": {"limits": {
                    "cpu": run["cpu"],
                    "memory": run["memory"],
                }},
            }],
            "scaling": {
                "min_instance_count": run["min_instances"],
                "max_instance_count": run["max_instances"],
            },
        },
        opts=pulumi.ResourceOptions(depends_on=[registry]),
    )
    gcp.cloudrunv2.ServiceIamMember(
        f"{name}-public",
        name=cloud_run.name,
        location=region,
        role="roles/run.invoker",
        member="allUsers",
    )
    pulumi.export(f"{name}_url", cloud_run.uri)

pulumi.export("registry_url", f"{region}-docker.pkg.dev/{project}/{registry_name}")
