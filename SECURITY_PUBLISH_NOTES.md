# Security Publish Notes

Prepared for public GitHub upload on 2026-05-31.

## Excluded

- Nested `.git` histories.
- Dependency folders: `node_modules`, `.venv`, `venv`, `env`.
- Build/runtime folders: `dist`, `build`, `target`, `.next`, `.cache`, `.tmp`, `.tauri`, `coverage`, `out`.
- Runtime/private data: `data`, `.opencode`, `.env`, local DB files, SQLite files, logs.
- Secrets and identity material: credential/cert files and token-bearing env files.
- Packaged binaries and heavy artifacts: `.exe`, `.dll`, `.msi`, archives, model binaries, generated voice outputs.
- Machine-specific runtime bundles such as embedded Node distributions.

## Sanitized

- Hardcoded Google/OpenRouter keys in copied files.
- Local paths referencing the user profile or the Digital Lab workspace.
- Build logs and crash logs that exposed local machine details.

## Notes

This is intended as a complete source-level public export, not a byte-for-byte backup. Local databases, embeddings, indexes, logs, dependencies, and generated outputs should be rebuilt from the source instructions.
