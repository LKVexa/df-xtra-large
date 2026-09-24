# DF Xtra Large

**1.0.1** (`DF-PA21.2-1.0.1`) by **RUSSELL PHILIP SMITHSON**. Apache License 2.0.

This is the separate delivery of `DF_Xtra_Large`: the `N_XLARGE` classical fabric node, embedding QUORUM LCTL/MSSL 2.1.0 and the Python-hosted QUORUM VM 5.0.0 candidate. Runtime ISA/ABI labels are retained for compatibility; the distribution version identifies the hardened derivation.

## Setup

Use Python 3.10 or newer in a virtual environment:

```sh
python -m pip install --only-binary=:all: -r REQUIREMENTS.txt
python -B tools/validate_release.py
python -B adapter/dfabric/cli.py node-verify
```

Portable validation checks every sealed file and runs manifest, adapter-path, signature, image, key-output, persistence and operational-world tests. Full native verification needs Linux/POSIX, GNU make, sha256sum and Java 21 for the bundled LCTL verifier. `python -B tools/validate_native.py` runs the VM and world regression suites in a temporary copy. CI tests Windows/Linux on Python 3.10 and 3.14, and the native node on Ubuntu with Python 3.12. Native prerequisites missing on Windows are not evidence of a native pass.

Run an example with `python -B adapter/dfabric/cli.py node-run examples/add42.lctlc`. This builds and signs local development artifacts. The included `DEV_ONLY_private_seed.hex` and matching trust store are public test fixtures, not secrets or production authority. Supply your own trust/key lifecycle for deployment. Do not use these development keys for confidential or production workloads.

## Changes and limits

Degenerate, noncanonical and off-curve Ed25519 points are rejected consistently before either backend. Signed images must satisfy instruction, capability, resource, version and algorithm checks. The declared entry point is honored. Step budgets are limited to 1–1,000,000. Signature verification is not a claim that arbitrary guest workloads are safe for a host: this is a Python reference process, not an OS sandbox.

JSON input/output is bounded to 16 MiB, source input to 8 MiB, and key input to 128 bytes. Input links/nonregular files are refused. Output files are atomically replaced and key creation never overwrites existing paths; POSIX private key files use mode 0600. Windows permissions inherit the chosen directory's ACL. A failed public-key write can leave the newly created private file. Use trusted local directories; same-user filesystem races are outside this boundary.

Dual-slot state generation now derives from authenticated records rather than the unauthenticated control file. Corrupt slots fall back to an older authenticated slot. This does not supply rollback resistance against an attacker able to restore both old slots. The pure-Python signing fallback remains non-constant-time; install the declared cryptography backend when timing confidentiality matters. Memory and trace growth depend on workload and service behavior despite the instruction-step limit.

## Provenance

`RELEASE_CONTENTS.sha256` inside the payload binds the current derivation; the original payload SHA256SUMS and MANIFEST remain historical. `node/PAYLOAD_DIGEST.json`, the root manifest and `FILES.sha256` bind the released bytes. `provenance/PAYLOAD_CHANGES.json` records every changed payload path. Historical qualification and performance records do not certify this release or physical hardware. This node supplies no physical QPU execution or production authority. External fabric/unified registry pins need deliberate integration for the new payload.

See [AUDIT.md](AUDIT.md), [CHANGELOG.md](CHANGELOG.md), [LICENSE](LICENSE) and [NOTICE](NOTICE).
