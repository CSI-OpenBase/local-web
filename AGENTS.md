# Python Project Guidance

Canonical remote: `git@github.com:CSI-OpenBase/local-web.git`

This repository is the source of truth for creator authorization, automatic data
table export, local video archives, user-triggered anonymized comment export,
persistence, backend APIs, and the local web UI. Windows and macOS hosts consume
this project as a wheel or frozen backend.

- Keep runtime data outside installed package directories.
- Keep this repository independently cloneable; do not require either desktop
  host repository to be present for installation, tests, or wheel builds.
- Preserve the authenticated desktop contract for `/health` and `/api/shutdown`.
- Treat exported creator data and browser sessions as sensitive local data.
- Do not introduce CSI Core scoring models, proprietary weights, benchmarks, or
  commercial report logic.
- Keep migrations and `LICENSE`/`NOTICE` resources present in built wheels.
- Do not commit `var/` data, `workspace-data/`, browser profiles, exports, or
  generated build artifacts.

Verify changes with:

```powershell
python -m pytest
python -m compileall -q admin_app scripts
python -m pip wheel . --no-deps --wheel-dir dist
```
