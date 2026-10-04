# Decision Provider v1 — Quickstart

The Decision Provider is the ecosystem's "semantic if": one swappable interface for the
engine's typed decision points (relevance judging, quality scoring, dedup candidate
selection, calibrated yes/no). Prepared canon-state goes in, a typed answer with
calibrated confidence and attribution goes out. The family precedent (wave W5d): a new
local provider was connected by shipping an artifact and a config flag — with zero
engine edits.

## Normative spec

- [spec.md](spec.md) — normative contract (Russian canon, RFC 2119 keywords).
- Full English mirror: [spec.en.md](spec.en.md).
- No machine schema in v1 — the contract fixes semantics, not wire (see §7 for the
  versioning plan).

## Key rules

- **Three primitives only** — `Choice` (option + confidence), `Score` (scale value +
  confidence), `Noul` (calibrated yes/no + confidence); typed answers, never prose.
- **Policy lives in the product** — the engine's code and config own the questions,
  `Choice` criteria and `Score` scales; the provider answers the question asked; a
  provider switch never changes policy.
- **Prepared canon-state only** — envelope + bodies of selected records per query; raw
  memory dumps never reach a provider.
- **Privacy gate is uniform** — `no-federate` and secret-bearing records never leave the
  storage; before any external call a mechanical scan (`danger_detectors`,
  `secrets_detector`) runs and any hit aborts the whole call.
- **Calibration before trust** — no implementation joins product decisions before
  passing the canon (vitals) calibration; locality grants no discount; an uncalibrated
  "confidence" is not a number.
- **Fail-open degradation** — any provider failure degrades to the `deterministic`
  baseline (whole provider, or a single verdict) with a machine-parseable warn from the
  implementation's namespace (engine precedent: `CORTEX-E-*`); the product path is
  never blocked.
- **Local-first by default** — the default implementation is `deterministic`; local
  routers have zero outbound traffic by construction and carry a weights fingerprint (a
  weight change = recalibration event); the external adapter is **off by default
  forever** and needs the owner's flag **plus** an API key.
- **A provider is not a supervisor component** — it is an in-process engine interface;
  no component manifest, no supervisor management.

## Examples

| File | Shows |
|---|---|
| [examples/example-decisions.txt](examples/example-decisions.txt) | the three primitives, fail-open degradation lines, a privacy-gate abort (illustrative placeholders, no wire format in v1) |

## Verify

v1 ships a human integrator checklist: [conformance/checklist.md](conformance/checklist.md)
(DP-01…DP-15) with spec-section references and verification methods. An executable
conformance suite arrives with the machine form of the interface (a minor contract
change). Until then: a green checklist + the canon calibration report are the gate for
joining product decisions.

## Status

`1.0.0-draft.1` — living interface migrated from vesma-canon ADR-0004 (2026-10-04,
roadmap phase 2; ADR ratified 2026-09-28). Becomes stable (`1.0.0`) with the first
conformant implementation in the `vesma` engine. Experimental verdicts, preregistrations
and measurements stay in vesma-canon (the evidentiary layer).

## See also

- [spec.md](spec.md) — full normative text: gates, failure classes, threat model, migration.
- [vesma-canon](https://github.com/vesmaro/vesma-canon) — ADR-0004, calibration methodology (private repo).
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — repo structure, contract discipline, the i18n rule.
