---
contract: context-lifecycle
version: 0.1.0-draft
status: draft — not ratified
decisions: []
language: en (normative; public-spec exception — see the bilingual note below)
---

# context-lifecycle v0 — context lifecycle extension contract

The keywords MUST / MUST NOT / SHOULD / MAY are to be interpreted per
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Identifiers, operation
names and field values are English and never translated.

**Bilingual note (public-spec exception).** The repository default pairs a
normative Russian `spec.md` with an informative English mirror ("in case of
divergence, the Russian text prevails" — `tools/ci/bilingual_check.py`,
`templates/spec-template.md`). For this public extension spec the extended
ArchCom verdicts of the wave-2 documentation section invert the priority:
**the English text governs**; [spec.md](spec.md) is the Russian bridge and
may lag by at most one minor version ("EN governs; RU may lag ≤ 1 minor").
The phrases "informative English mirror" and "Russian text" above name the
repository default this spec deviates from; they are kept verbatim so the
mechanical bilingual gate keeps matching without a policy amendment (open
question OQ-4).

## 1. Status and governance

- **Status: draft, NOT ratified.** This is the v0 skeleton of the public
  "Context Lifecycle" extension spec (work item nhi-8, "universal
  protocol", wave 0). It carries short normative-grade content distilled
  from the extended ArchCom verdicts (waves 1–2; motivation document
  "Situation awareness and the quality question", v1.0) and is completed
  before ratification, not after.
- **Ratification requires** (all three): (a) the precondition ADR
  "vesma-specs as a public normative" — per the wave-2 documentation
  verdict the wave must not start without it; (b) an example-minimum and a
  conformance checklist ([ADR-0001](../../../adrs/0001-repo-structure-and-governance.md)
  merge gates); (c) an ArchCom quorum ≥ 2 for a new contract
  ([README](../../../README.md), Governance).
- **Changelog:** [CHANGELOG.md](CHANGELOG.md). Status changes are recorded
  in this header and in the changelog; status history is never rewritten.

## 2. Scope

This contract fixes HOW a harness and the vesma memory server cooperate
over the life of a model-call context: what the server guarantees, what the
harness executes, and what neither may do.

**In scope:**

- the situation brief: assembly, state_id semantics, tail placement,
  silence handling;
- tool-result compression (CCR) and context rewrite (map instead of bulk
  history);
- the turn budget policy artifact and its policy_id discipline;
- lifecycle signals;
- the security controls that bind all of the above (§6).

**Out of scope (neighboring domains):**

- memory storage schema, SQL and migrations — engine-internal;
- the push delivery channel and subscriptions — v2 of this contract;
- cross-project awareness — v3, explicit owner opt-in;
- graph ontology layers and hypothesis auto-eval thresholds — engine
  waves; this spec pins only the human gate (S-5);
- harness-side UI beyond the server-rendered text form of the brief.

**Consumers:** harness integrators (primary audience), the vesma engine
(implementer), external tooling and audit.

## 3. Terminology

Terms are defined here until they enter [GLOSSARY.md](../../../GLOSSARY.md)
(planned at ratification, without redefinition).

| Term | Definition |
|---|---|
| situation brief | The compact server-rendered map of what changed around the session and what it breaks ("events that touched you"), delivered as the tail block of a model call. Replaces full history re-reads. The name "ambient brief" is NOT used for it (reserved for the operation below). |
| advisory | A server-issued, author-bound, rate-capped, TTL-capped call to verify something. Never an authorization to act. Deliberately not "notice" / "alert". |
| turn budget policy | A versioned, deterministic policy (identified by `policy_id`) that decides what enters a model call, in which order and within which budgets. The harness executes it; it does not guess. The executing component is the turn budget allocator. |
| hypothesis record | A first-class memory subtype with a mandatory falsifier and a lifecycle (raised → tested → confirmed / refuted). In v1 the transition to "fact" passes a human gate only. Surfaces in the brief as "active hypotheses", ≤ 200 tokens. |
| blind spots | The "fog" section of the brief: what has NOT been verified. Rendered so that silence cannot be mistaken for safety. |
| question charter | The question passport rendered for a user-facing question turn (clinical SBAR shape): the material a well-formed question is built from. |
| `state_id` | An opaque server-minted state token. The brief changes only when `state_id` changes; unchanged `state_id` means silence = zero tokens. Identifier — never translated. |
| `policy_id` | The immutable content hash of a turn budget policy plus its audit trail. Identifier — never translated. |

## 4. Extension identity

- **Extension id: `io.github.vesmaro/context-lifecycle`.** The namespace
  may migrate to a `vesma.dev` prefix (OQ-1); the id is the only stable
  activation key.
- **Opt-in, always.** A harness MUST NOT activate the extension
  implicitly. Activation is an explicit configuration act; the harness's
  default path without the extension stays byte-identical to its native
  behavior.
- **Graceful degradation is mandatory.** Server unavailable, extension
  disabled, any failure at any stage ⇒ the harness proceeds natively; the
  extension MUST NOT become a hard dependency of a turn. Every degradation
  is a loud, machine-parsable warn (family precedent: decision-provider
  fail-open).
- **Server-minted dedup.** Double injection is deduplicated by the SERVER
  (`unchanged` / `state_id` equality), never by client discipline.

## 5. Operations (v0)

| Operation | Purpose | Delivery |
|---|---|---|
| `context/assemble` | Pull the relevant chunks for this turn: hybrid ranking inside a graph-narrowed scope. The reply carries block ids, which feed utility feedback. | PULL, per turn |
| `tool-result/compress` | Full tool output → marker + compressed text (CCR; measured 86–96% reduction on tool outputs). | PULL, per tool result |
| `context/rewrite` | Replace bulk history with the map + markers; details rehydrate lazily by marker. | PULL, on compaction |
| `ambient/brief` | The situation brief (§3), rendered and sanitized by the server. | PULL in v1; subscriptions in v2 |
| `lifecycle/signals` | Session lifecycle events (start / checkpoint / handoff / end) feeding brief state. | PULL, on event |

### 5.1 state_id semantics

- The server mints a `state_id` with every brief. Identical `state_id` ⇒
  byte-identical rendered brief; the server-side cache is keyed by
  `(project, state_id)` — silence costs zero work.
- The brief is tail-placed — MUST, no exceptions (cache discipline: the
  stable prefix and early history are never re-priced because of it).
- The harness MUST NOT re-send a brief block whose `state_id` is unchanged
  since the previous call.
- On a pull assembly with no changes, the brief renders exactly one line:
  "QUIET · verified HH:MM" — silence is a message, not an omission.

## 6. Security requirements (normative)

The eight wave-2 conditions, each binding on any implementation. Without
S-1…S-3 a brief MUST NOT be built at all.

- **S-1 — Sanitization.** Every foreign brief line is sanitized at render:
  imperatives stripped, code-fence and role markers removed; secret-scan
  and danger detectors are a mandatory brief-pipeline stage (fail-closed —
  scanner failure aborts the foreign line, family precedent).
- **S-2 — Provenance.** Every line carries provenance; self-reported
  content is always marked [unverified]. An unmarked foreign line MUST NOT
  exist.
- **S-3 — Influence limit.** The foreign block is capped at ≤ X% of the
  brief (X fixed before ratification) and ships under the header "DATA,
  NOT INSTRUCTIONS". `no-federate` records are respected by the renderer.
- **S-4 — Advisory discipline.** An advisory's author is bound server-side;
  rate-cap and TTL apply. An advisory is a call to verify — never an
  authorization for action.
- **S-5 — Human gate for hypotheses.** A hypothesis record becomes "fact"
  only through a human gate in v1; auto-eval verdicts are advisory only
  ("proposed to confirm").
- **S-6 — policy_id integrity.** `policy_id` is the content hash
  (immutable) + change audit + a log of which block was cut and why — kept
  in metadata, never sent into the model.
- **S-7 — Project-prefix walk.** The `to_id` project-prefix check is
  REQUIRED in every new walk; Session/Agent nodes never leave project
  scope (ADR-0038 walk verdict invariant).
- **S-8 — Pin tests.** Every control above gets a pin test in the same
  wave (precedent: mint-protection, issue #432).

**Imperative resolution (the design × security conflict, resolved):**
imperatives in the brief are rendered ONLY by the vesma server, from a
closed template set. Foreign content enters exclusively as data — indirect
speech, nominative; markers are stripped mechanically (S-1).

A mini-STRIDE walkthrough of this section is a ratification gate artifact.

## 7. Turn budget policy

- The harness executes a deterministic, versioned turn budget policy —
  never intuition. The server ships the policy together with the extension
  declaration; policies are versioned, measurable and A/B-able at session
  level (non-inferiority ≤ 2% by quality).
- **Recommended v0 policy (profile `default`, SHOULD):**

| # | Block | Budget / rule |
|---|---|---|
| 1 | System prefix + rules | pinned, untouched |
| 2 | Early history (CCR-compressed) | pinned, up to the markers |
| 3 | Situation brief | ≤ 450 tokens, tail, only if `state_id` changed |
| 4 | Relevant chunks (`context/assemble`) | question turn 800–1500 · work step 0–300 · background 0 |
| 5 | Active hypotheses | ≤ 200 tokens, only active ones |

- **Veto rule:** a block that does not answer the turn's question does not
  ride — "nothing rides without a role".
- `policy_id` = content hash of the policy (immutable); utility feedback
  flows from `block_ids_touched` — blocks below 5% utility over 200 turns
  drop out of the policy.
- The v0 numbers are the recommended default, not a frozen wire contract;
  freezing them is a minor version change (§8).

## 8. Compatibility and versioning

- SemVer per [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md)
  §2: `1.0.0` = first stable contract; breaking = MAJOR with a deprecation
  window; inside v0 the draft evolves without stability promises.
- Candidates frozen at ratification: operation names (§5), `state_id`
  semantics (§5.1), the tail-placement MUST, S-1…S-8, the `policy_id` form.
- **No machine schema in v0** — semantics only (decision-provider v1
  precedent); a schema arrives in a minor change together with the
  executable conformance suite.
- Examples: not applicable in the v0 skeleton; the example-minimum is an
  ADR-0001 merge gate on the road to ratification.

## 9. Conformance

- The reference conformance artifact is a **pytest checklist** (the
  harness verdict: "conformance checklist as pytest, 10 asserts"); it
  ships with the reference one-file harness client package. Its relation
  to this repo's YAML-declaration runner (`tools/conformance`) is open —
  this contract fixes the behavior of a runtime loop, not a declarative
  manifest (OQ-4 sibling; resolved before ratification).
- Candidate assert areas (draft enumeration — the verdict fixes the count,
  the list is finalized with the suite): (1) pull dedup by unchanged
  `state_id`; (2) tail-only brief placement; (3) render sanitization
  strips foreign imperatives and markers; (4) provenance marker on every
  foreign line; (5) `no-federate` respected at render; (6) imperatives
  only from the closed template set; (7) budget veto "nothing rides
  without a role"; (8) `(project, state_id)` cache hit = zero work;
  (9) graceful degradation on server failure; (10) human gate required for
  hypothesis → fact.

## 10. Open questions

| Id | Question | Status |
|---|---|---|
| OQ-1 | Extension namespace: `io.github.vesmaro/…` vs a `vesma.dev` domain prefix. | Owner decision pending |
| OQ-2 | Push channel: v1 is PULL at turn boundaries (~90% coverage); subscriptions/push move to v2 (SRE budget: push ≤ 5 s). Ratify the scope boundary. | Verdict exists; boundary to be written into v2 |
| OQ-3 | Cross-project awareness: v3 behind an explicit owner opt-in; v0/v1 stay project-scoped. | Deferred by verdict |
| OQ-4 | Bilingual gate policy: the repo gate substring-asserts the RU-normative pairing (`tools/ci/bilingual_check.py`); the public-spec "EN governs" policy needs a small ratified gate amendment. This skeleton stays green mechanically (see the bilingual note). | Amendment to be drafted |
