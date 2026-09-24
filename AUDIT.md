# DF Xtra Large 1.0.1 audit

Work was performed in a separate copy; the supplied source folder is preserved.

## Repairs

- Reproduced identity-public-key/identity-signature acceptance with both the pure-Python and cryptography backends. Point decoding now checks canonical field/sign encoding, curve membership, identity rejection and prime-subgroup membership before backend verification. A bounded cache retains only public point decodings. Positive signing/execution and rejection tests cover both paths.
- Enforced signed image shape, ABI/resource declarations, numeric types (booleans are not integers), opcode operands, branch targets, capability bounds, signature algorithm, trust metadata and rollback-floor input. Direct VM construction also validates images and honors their entry point.
- Bounded file and JSON reads; rejected duplicate JSON/source keys and non-finite numbers. Bounded APDU text before conversion. New keys use exclusive creation and private POSIX permissions; existing paths are preserved.
- Replaced predictable state temporary files with unique, atomically replaced files. Generation comes from authenticated slots; MAC comparison uses compare_digest. Tampered control state cannot choose generation or slot paths.
- Applied the already-reviewed shared DF manifest and adapter output-name protections after verifying the supplied adapter files were identical. Preserved the PA-LCTL core pin.
- Added current payload checksums, a per-file derivation map, Apache-2.0 LICENSE/NOTICE, README and CI. Redacted a workstation path from a historical cross-reference diagnostic. Historical source/qualification version labels remain intact.

## Verification

New regression tests cover valid signed execution, both signature backends, malformed points and images, step limits and entry points, duplicate/non-finite JSON, existing keys, authenticated-state recovery, atomic-write failures and link/FIFO rejection. Existing VM tests require Java; Linux CI runs them with the bundled column verifier and the original world suites. Portable CI also exercises the 30-test operational-world reference suite. Original Linux-only resource and JVM-dependent tests cannot run on this local Windows host; those are covered by native CI rather than being described as local passes.

## Boundaries

This is a hosted reference implementation, not independently audited production cryptography or an OS process sandbox. The bundled Java verifier is retained, not rebuilt. Native world services may be expensive within the allowed guest step count; no host memory/cgroup isolation is supplied. State slot replay and same-user filesystem races remain possible within the documented local trust model. Each state file replacement is atomic, but cross-file updates and power-loss durability are not a transaction. Historical certification records are not new results. Read README.md before using the included public development keys.

Sources: [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) for encoding/verification behavior; [cryptography release](https://pypi.org/project/cryptography/50.0.1/) for the pinned optional backend.
