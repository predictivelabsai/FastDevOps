# FastDevOps repository instructions

This repository is the control plane for Fast* deployments. Read `README.md`,
`SKILLS.md`, and `config/services.yaml` before changing deployment behavior.

- Default to `validate`, `doctor`, `status`, API GETs, and `pulumi preview`.
- Do not deploy, restart, change environment variables, create applications,
  run `pulumi up`, or mutate GitHub/Coolify without explicit authorization.
- Treat Coolify UUIDs as opaque. Discover and copy them; never derive them.
- Never print secret values. `env` lists names only.
- Keep service definitions in `config/services.yaml`; Pulumi consumes that
  file rather than maintaining a second service list.
- Preserve confirmation gates. CI mutations require an explicit `--yes`.
- Before handoff run compile checks, CLI validation, skill validation, and
  inspect diffs for credentials and absolute developer paths.
