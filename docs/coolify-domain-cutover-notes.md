# Coolify / FastSME domain cutover notes (2026-09-08)

Inventory sync from `fast-domains-latest.csv` with safe cutovers only.

## Applied in `config/services.yaml`
- **fastclinic**: primary `domain` → `https://clinic.fastsme.com`; previous hosts kept under `domains:`.
- **fastvc**: primary `domain` / `SERVICE_URL` → `https://vc.fastsme.com` (live); `fastvc.org` kept as alias.
- **fastbi**: primary remains `https://fastbi.org` because `bi.fastsme.com` was DOWN externally at audit time. `bi.fastsme.com` listed under `domains:` as pending DNS — cut over only after DNS + health checks.

## Not cut over / not cataloged
- **pe / FastPE**: CSV primary `pe.fastsme.com` is pending DNS. Keep `pehero.chat` (or existing Coolify host) until DNS works. FastPE is **not** registered in `services.yaml` yet — do not invent Coolify UUIDs. CSV `Remote` corrected to `predictivelabsai/FastPE`.
- **factoring**: CSV filled with IP `191.218.164.166` and GitHub remote `predictivelabsai/FastFactoring`. Catalog already has `fastfactoring` → `https://fastfactoring.org`.

## CSV fixes applied in `data/fast-domains.csv`
- `pe` Remote: FastVC → FastPE
- `bi` Local: FastInsights → FastBI
- `factoring`: filled IP + Local + Remote when blank
