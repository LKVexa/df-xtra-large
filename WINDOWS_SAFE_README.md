# Windows-safe packaging notes

This distribution was repacked to eliminate legacy Windows `MAX_PATH` extraction failures and case-insensitive filename collisions.

- Maximum archive-internal file path target: **160 characters**.
- Verbose workflow directory names were compacted while requirement IDs in leaf filenames were retained wherever possible.
- The Linux-distinct `vm/world/evidence/input_provenance.json` case collision was renamed to `input_provenance_summary.json`; `INPUT_PROVENANCE.json` remains unchanged.
- Python `__pycache__` / `.pyc` artifacts were removed because they are platform-specific generated files.
- `BUILD.cmd`, `RUN.cmd`, and `VERIFY.cmd` use `pushd`/`popd` so UNC paths and paths containing spaces are handled safely.
- Run `WINDOWS_PATH_CHECK.cmd` after extraction to validate the actual extraction root against the legacy 260-character path budget.
- `WINDOWS_PATH_MAP.json` records every renamed delivered path.

For maximum compatibility with tools that still enforce legacy `MAX_PATH`, keep the extraction destination reasonably short (for example `C:\DF\`).
