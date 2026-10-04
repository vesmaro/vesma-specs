---
contract: decision-provider
version: 1.0.0-draft.1
status: draft (ratified by implementation)
decisions: [ADR-0001, vesma-canon ADR-0004]
language: en (informative mirror)
---

# decision-provider v1 — decision provider contract (the "semantic if")

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian text
> prevails. The mirror is maintained in the same change as the Russian text
> (single-commit sync policy).
>
> **Translation note.** Translation base: vesma-specs `main` HEAD
> `f6f9d206ec8f3a0700574a91cca1f453b49571cb` (2026-10-04), the revision at
> which this living contract was migrated from vesma-canon ADR-0004
> (roadmap phase 2).

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
RFC 2119. The normative prose is Russian; identifiers, primitive names and
field values are English.

**Bilingual pair (mandatory).** The normative canon is [spec.md](spec.md)
(RU); this file is the informative EN mirror (single-commit sync); the
integrator quickstart is [README.md](README.md). The i18n rule — ADR-0001 §5.

## 1. Scope

A decision provider is a swappable implementation of the engine's typed
decision points: judging record relevance, scoring quality against the
canon, selecting a deduplication candidate, answering a calibrated
yes/no. There is one interface — the "semantic if": prepared canon-state
in, a typed answer with calibrated confidence and attribution out. The
consumers program against the interface, not against a concrete provider:
today deterministic heuristics decide, tomorrow a local model, someday an
external service — with no engine edits (the in-house precedent of a
contract family is wave W5d: a local provider was connected by shipping an
artifact and a config flag).

**In scope:**

- the three interface primitives: `Choice`, `Score`, `Noul` (§3.2);
- the family-wide contract rules: policy at the product level, input
  shape, the privacy gate, the calibration gate (§3.3–§3.6);
- the family of implementations and their activation conditions:
  deterministic baseline, local, external (§3.7);
- the fail-open degradation semantics and answer attribution
  (§3.8–§3.9);
- failure classes and the receiver's mandatory reaction (§4).

**Out of scope:**

- the transport shape of the call and the response format — v1 fixes
  semantics, not wire; a machine schema arrives as a separate minor/major
  contract version (§7);
- the calibration methodology and artifacts — preregistrations, corpora,
  thresholds, run verdicts, baseline measurements — belong to vesma-canon
  (the evidentiary layer); the contract fixes only the "calibration before
  trust" gate and a pointer to the methodology;
- the concrete questions, `Choice` criteria and `Score` scales — owned by
  the product (engine code and config), not fixed by this contract
  (§3.3);
- launching/stopping/health of providers as processes — the domain of
  `specs/service-lifecycle/v1`; a provider is an in-process engine
  interface, not a supervisor-managed component (see §3.10);
- pricing, limits and fitness of external services — reference analyses
  stay in canon.

**Consumers:** the `vesma` engine (decision points: dedup guards,
awareness hints, quality thresholds), vesmaro-agent and future ecosystem
consumers, provider implementors (local models, external-service
adapters).

### 1.1 Origin

The living version of the interface was migrated from vesma-canon ADR-0004
(2026-10-04, roadmap phase 2 of vesma-specs); canon keeps the history and
the pointer. Contract-suitable material was carried over: the interface
and primitives, the family of implementations, ADR rules 1–4, the fail-open
degradation semantics (the CORTEX-E precedent, wave W5d), telemetry
attribution. Left in canon: experimental verdicts (including the declined
W4c calibration), preregistrations and their addenda, corpora and
measurements, the external-service pricing analysis, wave sequencing. The
W5a addendum on the local surface is carried over in substance (zero
network, dataset-export hygiene, weights fingerprint — §3.7); its history
stays in canon.

## 2. Terminology

General terms — the [glossary](../../../GLOSSARY.md). Contract terms of
this document:

| Term | Meaning |
|---|---|
| decision provider | a swappable implementation of the "semantic if" interface: answers the product's typed question over prepared canon-state |
| decision primitive | one of the three typed question forms: `Choice`, `Score`, `Noul` |
| `Choice` | selecting an option by given criteria → the selected option + confidence |
| `Score` | scoring on an ordered scale → the scale value + confidence |
| `Noul` | a calibrated yes/no → yes/no + confidence |
| prepared canon-state | the envelope + bodies of the selected records, assembled for a specific query; the only permitted provider input |
| baseline implementation (`deterministic`) | the engine's deterministic heuristics formalized as the first implementation of the interface; the calibration base and the degradation target |
| calibration | verification of an implementation per the canon methodology (vitals): preregistration, an honest baseline, measurement on ecosystem data; the gate for participating in product decisions |
| confidence | a number that has meaning only for a calibrated implementation (§3.6) |
| fail-open degradation | the failure-semantics requirement: a provider error switches work to the baseline and never blocks the product path (§3.8) |
| attribution | stating, in every answer and in the log, who answered: primitive, implementation, confidence (§3.9) |
| weights fingerprint | the hash of the local model artifact in the run report; a weight change is a recalibration event (§3.7) |
| privacy gate | the rule uniform for all providers: records tagged `no-federate` and records containing secrets never leave the storage (§3.5) |

## 3. Contract

### 3.1 One interface

- **MUST**: all typed decision points of the engine be programmed against
  the decision-provider interface, not against a concrete implementation.
- **MUST NOT**: consumers call implementations directly bypassing the
  interface; provider switching is configuration, with no consumer code
  edits.
- **MUST**: every answer carry attribution — who answered (the
  implementation) — together with the answer (§3.9).

### 3.2 Primitives

- **MUST**: the interface expose exactly three primitives: `Choice`
  (option selection → option + confidence), `Score` (scoring on an ordered
  scale → scale value + confidence), `Noul` (a calibrated yes/no →
  yes/no + confidence).
- **MUST**: answers be typed — free text is not an answer; an
  implementation that can only answer in prose does not conform.
- **MUST NOT**: the provider generate and/or rewrite memory record bodies;
  the style canon stays with people and agents (the W5a addendum rule,
  carried into §3.7).
- New primitives are an additive contract change (a minor version, §7).

### 3.3 Policy lives at the product level

- **MUST**: the questions, the `Choice` criteria and the `Score` scales
  be fixed in engine code and config (the product), not in the provider
  API.
- **MUST**: the provider answer the question asked, not invent what to
  ask about.
- **MUST**: switching the provider not change the policy — questions,
  criteria and scales are invariant to the implementation.

### 3.4 Input — prepared canon-state only

- **MUST**: the provider input be prepared canon-state: the envelope +
  bodies of the selected records, assembled for a specific query.
- **MUST NOT**: raw memory dumps be handed to a provider — ever.
  The contractual rationale: dumps degrade accuracy (context rot), open
  an instruction-injection surface and would inflate the cost of shipping
  state.

### 3.5 The privacy gate is uniform for all providers

- **MUST**: records tagged `no-federate` and records containing secrets
  never leave the storage — for every implementation, including local
  ones (the `no-federate` tag is a canon storage/federation rule and holds
  regardless of provider locality).
- **MUST** (external calls): before any outbound call — a mandatory
  mechanical scan of the prepared state for secrets and dangerous
  content; the engine detectors are reused (`danger_detectors.detect`,
  `secrets_detector.detect_secrets`).
- **MUST**: a hit of any class abort the entire call, not excise a
  fragment.
- **SHOULD** (local implementations): the secrets scan as hygiene of
  calibration dataset export — the dataset is a separate copy of the
  data; records with secrets and `no-federate` never enter it (the
  procedure is frozen by the canon preregistration).

### 3.6 Calibration is mandatory before trust

- **MUST NOT**: any implementation participate in product decisions
  before passing calibration per the canon methodology (vitals):
  preregistering the hypothesis and thresholds before the run, an honest
  baseline against the current heuristics, measurement on ecosystem data.
  The methodology and its artifacts belong to canon; the contract fixes
  the gate.
- **MUST**: locality grant no discount — "trust without evidence" is
  forbidden equally for local and external providers.
- **MUST**: the "confidence" of an uncalibrated provider not be consumed
  as a number.
- **MUST**: a calibrated provider make sense only where it measurably
  outperforms the baseline heuristic (the holdout superiority condition —
  per the frozen canon preregistration).

### 3.7 The family of implementations

| Implementation | Status | Contract conditions |
|---|---|---|
| (a) `deterministic` — the engine's deterministic heuristics | the base, live since formalization | zero cost, zero external calls; the same primitives, deterministic rules; the calibration baseline for (b)/(c) and the degradation target (§3.8) |
| (b) a local router (the `mnema` model family) | optional, flag-gated | local-first: weights on the machine, inference and calibration are **zero-network**; provenance — the weights fingerprint in the run report; retraining/a weight change = a recalibration event |
| (c) an external adapter (e.g. the Jev family) | optional, **off by default forever** | a double activation gate: an explicit owner flag in the config **and** an API key; once enabled, §3.4–§3.6 apply without exceptions; the state is billed in full per query (limits — the canon analysis) |

- **MUST**: the default implementation be (a) `deterministic`; enabling
  (b)/(c) requires explicit configuration.
- **MUST**: implementations (a) and (b) have no outbound traffic — by
  construction; an outbound call from a non-external implementation is a
  contract defect (precedent: the AST tripwire on network imports in the
  engine implementation, W5d).
- **MUST NOT**: the (c) activation gate be satisfied by one of the two
  conditions — a flag without a key or a key without a flag do not
  activate the adapter.

### 3.8 Fail-open degradation

- **MUST**: any provider error degrade to the baseline: a
  load/metadata/pin artifact defect — the implementation as a whole
  switches to (a) `deterministic`; an inference/schema failure on a
  specific request — the single verdict degrades to the deterministic
  rule.
- **MUST NOT**: a provider failure block the product path (ingest,
  deduplication, hints) — ever.
- **MUST**: every degradation be logged machine-parseably, with a code
  from the implementation's namespace (precedent: `CORTEX-E-*` in the
  engine implementation, W5d) and the action named
  (`provider-degraded` / `verdict-degraded` / `call-aborted`).
- **SHOULD**: a weights-pin defect (fingerprint mismatch) be treated
  loudly as a recalibration event — a load refusal with `code=`, never a
  silent artifact swap.

### 3.9 Telemetry attribution

- **MUST**: every provider answer be logged machine-parseably: primitive,
  implementation, confidence — in the same discipline as the canon
  telemetry; this is the raw material for a strict strict-default.
- **MUST**: the telemetry line make it possible to answer "who made this
  decision" without reading the code (attribution in the data, not in
  guesses).

### 3.10 A provider is not a supervisor component

- A decision provider is an in-process engine interface, not an ecosystem
  component: no `specs/component-manifest/v1` manifest is filed for it, it
  is not managed by the supervisor. Its semantic family is degradation
  instead of falling over (the tier philosophy of
  `specs/service-lifecycle/v1`): a provider failure lowers decision
  quality but never takes the system down (§3.8).
- **MUST NOT**: the provider call be pushed onto the hot path as a
  network call to a component process — the interface is in-process;
  inline external-LLM calls at decision points were rejected by ADR-0004
  (uncontrollable cost and latency, free-text answers, calibration
  impossible by construction).

### 3.11 Format freeze untouched

- **MUST**: the interface consume canon records as they are — the
  envelope, types and sections are unchanged; the schemas are not edited.
- **MUST NOT**: the interface require storage-format changes for its own
  convenience.

## 4. Error codes

v1 does not fix a full error-code registry: the transport shape and the
response format are not frozen in v1 (§7), and literal codes belong to the
implementations' namespaces (the engine precedent — `CORTEX-E-*`). The
contract fixes the failure classes and the mandatory receiver behavior —
an implementation may refine codes within a class, but not the semantics:

| Failure class | Meaning | Source | Mandatory receiver reaction |
|---|---|---|---|
| `<impl>-PIN` (class) | artifact defect: the weights/metadata/schema fingerprint did not match the pin | provider loader | full provider degradation → (a) `deterministic`; a loud machine-parseable warn; ingest not blocked; a recalibration event |
| `<impl>-INFER` (class) | an inference or answer-schema failure on a specific request | provider execution | the single verdict degrades to the deterministic rule; a warn; the answer is attributed to the baseline implementation |
| `<impl>-GATE` (class) | a privacy-gate hit before an external call (secret / dangerous content) | the pre-call scan pass | the external call is aborted entirely; no external traffic; a warn with the `call-aborted` action |
| `<impl>-CONFIG` (class) | an activation attempt violating the gate (flag without key, key without flag, unknown provider name) | config loader | the configuration is rejected; the active implementation remains `deterministic`; a warn |

## 5. Examples

The minimum example is mandatory (ADR-0001 §1). The transport shape is not
frozen in v1, so the example is illustrative — it shows the kind of content
of a question/answer/degradation, not a wire format:

| File | Shows |
|---|---|
| [examples/example-decisions.txt](examples/example-decisions.txt) | the three primitives (question → typed answer with confidence and attribution), fail-open degradation (provider/verdict), the privacy-gate abort — all values are placeholders |

## 6. Conformance

The executable `tools/conformance` runner validates declarations
(manifests, JSON schemas) — this contract has no machine declarations in
v1 (§1, §7), so the v1 conformance suite is the human integrator checklist
[conformance/checklist.md](conformance/checklist.md) (DP-01…DP-15), with
references to spec sections and verification methods. An executable suite
arrives together with the machine form of the interface — as a separate
minor contract change; until then a green checklist + the canon
calibration report are the gate for an implementation to participate in
product decisions (§3.6).

## 7. Compatibility

- **SemVer**: `1.0.0-draft.1` → `1.0.0` upon ratification by an
  implementation in the vesma engine. A breaking change = MAJOR + a
  deprecation window of `max(90 days, 2 minor releases)` with dual
  support (ADR-0001 §2); below 1.0 the window is 14 days.
- **Additive (minor)**: new primitives beyond the three; a machine form
  of the interface (schema/ + an executable conformance suite); new
  contract failure classes.
- **Breaking (MAJOR)**: changing the semantics of the primitives, changing
  the gates of §3.5–§3.7, abandoning fail-open degradation.
- **Consumers**: the `vesma` engine (decision points), vesmaro-agent; the
  family relation — the manifest/supervisor do not touch providers
  (§3.10), the layout is not involved (local model weights are a package
  artifact; the shipping discipline belongs to the engine).
- **Deliberately deferred beyond v1**: the transport shape and the
  question/answer schema; an executable conformance suite; provider
  artifact signatures (v1 provides only the weights fingerprint — the
  pin precedent in the engine implementation); external adapter
  quotas/limits.

## 8. Threat model (mini-STRIDE)

Assets: memory storage content (including `no-federate`/secrets), the
typed verdicts influencing product decisions, the integrity of local model
weights. Boundaries: engine ↔ provider (in-process); engine ↔ external
service (implementation (c) only, off by default); engine ↔ calibration
data (dataset export).

| Category | Threat | Mitigation | Check |
|---|---|---|---|
| **T**ampering | instruction injection through the provider input | the input is prepared canon-state only (§3.4); raw dumps are forbidden; a mechanical dangerous-content scan before an external call (§3.5) | DP-04, DP-05 |
| **T**ampering | a silent swap of local model weights | the weights fingerprint in the run report; a pin mismatch = a loud load refusal + a recalibration event (§3.7, §3.8) | DP-12, DP-08 |
| **I**nformation Disclosure | memory leaking through the external adapter | the privacy gate: `no-federate`/secrets never leave the storage (§3.5); a scan before every external call, a hit aborts the call entirely; the default is local implementations with zero network | DP-05, DP-11, DP-12 |
| **S**poofing | "who actually answered?" — verdict source substitution | mandatory attribution of every answer and machine-parseable telemetry (§3.9) | DP-09 |
| **R**epudiation | "why did the system decide this?" — an untraceable decision | decision telemetry in the canon discipline: primitive, implementation, confidence on every answer (§3.9) | DP-09 |
| **D**enial of Service | a provider failure/hang blocks ingest and the hot path | fail-open degradation: the provider or the single verdict switches to the baseline; the product path is never blocked (§3.8); inline external LLMs on the hot path are rejected (§3.10) | DP-07, DP-08 |
| **E**levation of Privilege | an uncalibrated provider influences product decisions | the calibration gate with no locality discount (§3.6); the `deterministic` default; non-baseline implementations are flag-gated; the external one is flag + key (§3.7) | DP-06, DP-10, DP-11 |

Every mitigation is covered by a DP-01…DP-15 checklist item or marked as
an engine check; there are no silent unverifiable promises.

## 9. Migration from legacy

The legacy here is the engine's decision points before interface
formalization: scattered heuristics called directly in code, and the
practice of "a model in production without calibration". The migration
belongs to the engine; the contract fixes the target shape and the order:

| Legacy pattern | Contract answer |
|---|---|
| an inline heuristic at a decision point (dedup guard, awareness hint, quality threshold) — called directly, without an interface | formalization as implementation (a) `deterministic` behind the interface (§3.7); the consumer programs against the primitive (§3.1) |
| the "confidence" of an unverified model in a product decision | the calibration gate §3.6: until calibrated — baseline only; an uncalibrated confidence is not a number |
| an external call on the hot path without a gate | the flag+key double gate (§3.7) + the privacy scan before every call (§3.5); by default — zero external calls |
| a silent model failure (silent quality degradation) | fail-open with a loud machine-parseable degradation (§3.8) — the failure is visible, quality drops to the baseline, not into the unknowable zone |
| a model editing/rewriting record bodies | the §3.2 prohibition: the provider answers with a verdict; bodies stay with people and agents |

Order: formalize (a) behind the interface → telemetry attribution on all
points (§3.9) → the calibration baseline (canon, the vitals methodology)
→ connect (b)/(c) behind a flag with the §3.6–§3.7 gates → retire the
inline patterns. The migration precedent is W5d: a local provider was
connected by shipping an artifact and a config flag with no engine edits.

## 10. References

- [spec.md](spec.md) — the normative Russian specification.
- [README.md](README.md) — the integrator EN quickstart.
- [conformance/checklist.md](conformance/checklist.md) — the DP-01…DP-15 checklist.
- [examples/example-decisions.txt](examples/example-decisions.txt) — the minimum example.
- vesma-canon, `docs/decisions/0004-decision-provider.md` — the migration
  source: the full decision history, the W5a addendum, rejected
  alternatives (the private
  [vesmaro/vesma-canon](https://github.com/vesmaro/vesma-canon) repository;
  canon keeps the history and the pointer).
- vesma-canon, `docs/experiments/provider-calibration-v2-preregistration.md`
  and `docs/experiments/provider-baseline.json` — the calibration
  methodology and artifacts (canon is their home; the §3.6 gate).
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — layer
  structure and governance: SemVer, the conformance gate, i18n (§5), the
  secrets policy (§6).
- `specs/service-lifecycle/v1` — the degradation-instead-of-failure
  philosophy (core/optional tiers); a provider is not a supervisor
  component (§3.10).
- `specs/component-manifest/v1` — the ecosystem component contract; it
  does not extend to providers (§3.10).
- The [glossary](../../../GLOSSARY.md), the [ecosystem map](../../../ECOSYSTEM.md),
  the [roadmap](../../../docs/roadmap.md) (phase 2 — the living-contract
  migration).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — the keyword
  interpretation.
