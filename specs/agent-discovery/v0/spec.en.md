---
contract: agent-discovery
version: 0.1.0-draft
status: draft
decisions: [ADR-0001, ADR-0002, "AGW-25 — addendum «discovery v6, models fleet leg» in docs/PROTOCOL.md §3 (vesmaro/vesma-agent, main (merge b98960e))", "gate 1 — discovery-contract-draft.md (vesmaro/vesma-eyes, feat/models-fleet-blueprint, daf969b)", "gate 2 — security-verdict.md (same, 832cd7a)", "gate 3 — ux-blueprint.md (same, cb166a8)", "owner directive 2026-10-28 («update the contracts and documentation» in vesma-specs)"]
ratified: |-
  Not ratified (draft). Authority trail: the agent leg is already merged
  as protocol amendment AGW-25 in vesmaro/vesma-agent (main (merge b98960e)
  branch, the «discovery v6» addendum in §3 docs/PROTOCOL.md); the red
  lines are ratified by gate 2 (security-verdict, 832cd7a, amendments
  1–2 to OQ-4); the wire shape is ratified by gate 1
  (discovery-contract-draft, daf969b); the mirror consumer is ratified
  by gate 3 (ux-blueprint, cb166a8 — MF1/MF2). Contract ratification as
  stable = the first conformant implementation of both legs: the agent
  leg (merged) and the board mirror (ingest into `GET /api/models`, the
  `discovered` zone — not merged yet; the target `ModelsDiscoveredItem`
  schema is already served by the board, the zone is honestly empty).
language: en (informative mirror)
---

# agent-discovery v0 — the model discovery contract (agent → board)

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian
> text prevails. The mirror is maintained in the same change as the
> Russian text (single-commit sync policy).
>
> **Status: draft (0.1.0-draft).** The contract codifies the already
> merged agent leg — protocol amendment AGW-25 «Models-fleet addendum —
> discovery v6» in `docs/PROTOCOL.md` §3 of the outbound ЦУП agent
> `vesmaro-agent` — as an ecosystem contract of the spec layer (owner
> directive 2026-10-28). The board mirror (ingest into `GET /api/models`)
> is provided for by the contract but not merged yet — see §9. Form
> changes after ratification go through the SemVer process only
> (ADR-0001 §2).

The key words MUST / MUST NOT / SHOULD / MAY are interpreted per
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Prose is English;
identifiers, fields and enum values are EN. Every requirement traces to
the AGW-25 amendment or fleet gates 1–2, marked «(AGW-25)»,
«(gate 1 §…)», «(gate 2 §…)».

## 1. Scope

The contract fixes the **wire discipline of the `models` field** — the
additive top-level field of the discovery report
`POST /api/executors/{executor_id}/discovery` of the outbound ЦУП agent:
which provider/model facts the agent may read from the host, how it
normalizes them, what it must sacrifice on leak suspicion, and what the
board does with the report at ingest. Principle: **names only** —
provider/model names and the endpoint URL are facts; credential
material is never a fact.

**In scope:**

- the shape of the additive top-level `models` field (`installations[]`,
  `notes`) and of the `installation` row (§3.2);
- names-only config reads through the built-in per-harness layout
  table (§3.3);
- `base_url` normalization: query/fragment/userinfo and
  credential-shaped query parameters always stripped (§3.4);
- `auth` — an enum fact from field PRESENCE, never values (§3.5);
- caps and shrink-to-fit: 64 rows, 50 models, 16 KiB object, 8 KiB
  per-file read cap (§3.6);
- the anonymous probe leg: loopback-only, fixed port table (§3.7);
- leak discipline: the names-only validator, row drop before marshal,
  loud local log with the value suppressed (§3.8);
- the `discovery_models: auto|off` knob (§3.9);
- snapshot semantics and the absent-field vs empty-field distinction
  (§3.10);
- board ingest duties: drop+audit of unknown dictionary values, honest
  422 on caps, the incident detector (§3.11);
- the route's error codes for this field (§4).

**Out of scope (neighbouring domains):**

- provider credential storage, sharing grants, the pull proxy — gate 2's
  verdict (`security-verdict.md` H1/H2, vesma-eyes); the contract stays
  correct if the owner answers the proxy «never» (gate 1 §4.5,
  gate 2 §4.10);
- roster UX (`GET /api/models`, the `discovered`/`providers`/`board`
  zones, provenance badges) — gate 3 (`ux-blueprint.md`, MF1/MF2);
- the other discovery-report fields (`harnesses`, `environments`,
  `k8s_*`) and the v3/v4/v5 legs — the norm of `docs/PROTOCOL.md` §3
  vesma-agent, not re-litigated here;
- the route transport as a whole: executor-token class, identity-match,
  the 60/60 s budget, 404-silence — inherited and fixed in §3.1 as-is
  (introduced by vesma-eyes 1.38.0, ME-015).

**Consumers:** the `vesmaro-agent` agent (field writer), the
`vesma-eyes` board (ingest reader, mirror and roster), third-party
agent integrators, the layer's conformance runner.

## 2. Terminology

The terms **provider**, **model**, **installation**, **discovery**
(the agent → board leg) are defined in the
[glossary](../../../GLOSSARY.md) and not redefined here: a models-fleet
provider is an external model-serving endpoint the owner connects — not
a «decision provider» of `specs/decision-provider/v1` (see the
glossary disambiguation). Contract-local terms:

| Term | Meaning |
|---|---|
| `auth` | An enum fact of credential-marker PRESENCE in the config: `configured` \| `anonymous` \| `unknown`. The credential value is never read, never leaves the machine (§3.5). |
| `source` | Origin of the installation row: `config` (names read from the harness config) \| `probe` (a local model server answered a models-list request). No third value exists (AGW-25). |
| `exec_env` | The frozen surface vocabulary: `metal` \| `distrobox:<name>` \| `pod:<name>` (the discovery v4 precedent). In this wave, `models` rows carry only `"metal"` (§3.2). |
| layout table | The agent's built-in per-harness table naming — at JSON-pointer / section-path level — exactly the fields of each config the agent may read (§3.3). |
| quiet zero | An honest absence that is not an error: logged no higher than info, never retried, never an error verdict (§3.6, §3.7). |
| shrink-to-fit | The agent's cap discipline: the object shrinks BEFORE send so it always fits; an over-cap send is impossible by construction (§3.6). |
| 404-silence | The agent's fallback on a board without the route (pre-1.38): the POST fails — nothing logs above info (§3.1). |
| no-wipe | The distinction between an absent field (= the leg did not report, mirror untouched) and a present-but-empty field (= a real zero-and-ran, the mirror is wiped) (§3.10). |
| names-only validator | The final pre-marshal filter: length caps plus a credential-shape scan of every emitted string (§3.8). |
| zero-and-ran | A report saying «the leg ran and honestly found no installations»: `models` present, `installations` empty (§3.10). |

## 3. Contract

### 3.1 Transport: one additive field on the existing route

- **MUST**: provider/model facts travel ONLY as the additive top-level
  `models` field of the `POST /api/executors/{executor_id}/discovery`
  body, next to `harnesses` (and the other additive fields of the
  family). No new route, no new timer, no new auth class, no new event
  channel (AGW-25; gate 1 §2).
- **MUST**: the leg rides the existing discovery cadence (the hourly
  pass + one POST at loop start) — `models` has no schedule of its own
  (AGW-25; gate 1 §2.3).
- **MUST**: the route's auth class and identity-match are unchanged:
  this executor's token; URL id ≠ token identity → `403`; revoked →
  `403`; pending MAY report; an authenticated report ticks `last_seen`
  (inherited from the deployed route semantics, vesma-eyes 1.38.0).
- **MUST**: on a board without the route (pre-1.38) 404-silence holds —
  the agent logs no higher than info and does not retry outside the
  normal cycle (§2; AGW-25 confirms unchanged).
- **MUST**: a board that ignores `models` stays conformant: the additive
  unknown field is accepted and ignored (the additive rule, §5 of
  vesma-agent; gate 1 §2.1).
- **MUST NOT**: the `models` field never creates registry rows, never
  extends allowlists, never changes routing, never creates credential
  records — discovery mirrors a fact, it does not grant authority
  (gate 1 §4.3; «advisory, never authority» — §3's own first sentence
  in vesma-agent).

### 3.2 Shape of the `models` object and the `installation` row

The form (additive; `notes` — omitempty):

```json
{"models": {"installations": [
  {"provider": "openrouter",
   "base_url": "https://openrouter.ai/api/v1",
   "auth": "configured",
   "models": ["z-ai/glm-4.6"],
   "harness": "codex",
   "exec_env": "metal",
   "source": "config",
   "note": "default model from harness settings"}],
 "notes": {"default_model": "z-ai/glm-4.6"}}}
```

- **MUST**: `installations[]` — rows of the form
  `{provider, base_url, auth, models[], harness, exec_env, source,
  note}`; the `note` field — MAY, omitempty, free text of fact.
- **MUST**: `provider` — the name/slug the local config uses, verbatim,
  ≤ 60 chars (AGW-25; gate 1 §2.1).
- **MUST**: `models[]` — a sorted list of model ids (the strings the
  provider's API expects, e.g. `z-ai/glm-4.6`), ≤ 50 per row
  (AGW-25; gate 1 §2.1).
- **MUST**: `harness` — for `source: config` rows, the harness-dictionary
  spelling (the owner of the read config); for `source: probe` rows the
  merged AGW-25 leg carries the probe source's slug (the provider name,
  e.g. `ollama` — the merged code's behavior,
  `internal/discovery/models.go`); in both cases the board drops and
  audits ad-hoc names by the same §3.11 rule — the merged code makes no
  probe-row carve-out (gate 1 §2.4).
- **MUST**: `exec_env` — only `"metal"` in this wave: distrobox/pod
  config surfaces are NOT read (honest absence; the v4/v5 container
  legs are untouched). The rest of the vocabulary belongs to future
  waves (AGW-25).
- **MUST**: `source` ∈ `config` | `probe` — no third value (AGW-25).
- **MUST**: `notes` — only facts the layout table names; today that is
  the harness's default-model pointer (`default_model`) (AGW-25).
- **MUST**: the top-level `models` field — one per report; the
  harness/exec_env attribution lives IN the rows (OQ-2 decision:
  top-level with explicit attribution, not per-environment;
  gate 1 §5 OQ-2).

### 3.3 Names-only config reads: the layout table

- **MUST**: a harness config is read ONLY through the built-in
  per-harness layout table, which names — at JSON-pointer / section-path
  level (e.g. `.providers.<name>.name`, `models[]` keys) — exactly the
  fields read; the decode's field set IS the table
  (gate 2 §2, amendment 1; AGW-25).
- **MUST NOT**: parse-and-scan heuristics («read the file, look for
  model-looking strings») are forbidden (gate 2 §2, amendment 1;
  AGW-25).
- **MUST**: the table is built-in and versioned in the agent — the v3
  fingerprint-table precedent (gate 1 §2.2; gate 2 §2 item 3).
- **MUST**: this build's table set is exactly:
  - codex `~/.codex/config.toml`: `model`, `model_provider`,
    `model_providers.<name>.{name, base_url, env_key}`;
  - continue `~/.continue/config.json`:
    `models[].{provider, model, apiBase, apiKey}`;
  - claude-code `~/.claude/settings.json`: `model`; from `env` — only
    KEY NAMES with the `ANTHROPIC_` prefix;
  - aider `~/.aider.conf.yml`: `model`, `openai-api-base`,
    `openai-api-key`;
  - zcode — deliberately ABSENT: no documented model-catalog path was
    determinable for this build (small-and-true beats broad-and-guessed)
    (AGW-25).
- **MUST**: extending the table (a new harness, a new field) is a
  contract change per §7; silently reading an unnamed field is a
  violation (gate 2 §2, amendment 1).

### 3.4 `base_url` normalization

- **MUST**: `base_url` reduces to `scheme://authority[/base-path]`
  (AGW-25; gate 2 §2, amendment 2).
- **MUST**: query and fragment are ALWAYS stripped (AGW-25; gate 2 §2,
  amendment 2).
- **MUST**: userinfo is stripped (AGW-25; gate 1 §2.1).
- **MUST**: a credential-shaped query parameter (`key=`, `api_key=`,
  `token=`, `access_token=`, … — detection by the PRESENCE of the
  parameter name, never its value) downgrades the fact to
  `scheme://authority` (host-only redaction) or to omission — the value
  is never echoed (AGW-25; gate 2 §2, amendment 2; gate 1 §2.1).
- **MUST**: an unparsable or authority-less URL is omitted (honest
  absence), never guessed (AGW-25; gate 1 §2.1).
- The board's rule is symmetric: the provider POST validates and strips
  credential-in-URL (userinfo or `?key=`) by the same amendment 2 —
  outside the agent wire, for boundary symmetry (gate 2 §4.5).

### 3.5 `auth` — an enum fact from field presence

- **MUST**: `auth` ∈ `configured` | `anonymous` | `unknown` and is
  derived ONLY from the PRESENCE of the credential-marker fields the
  table names (§3.3); the values of marker fields are never read into
  the payload in any encoding (AGW-25; gate 2 §2 item 3).
- **MUST**: the per-harness derivation for this build is exactly
  (AGW-25):
  - codex: `env_key` non-empty → `configured`; absent → `anonymous`;
  - continue: the `apiKey` field present → `configured`;
    null/absent → `anonymous`;
  - claude-code: an `ANTHROPIC_*` env KEY NAME → `configured`; none →
    `unknown`;
  - aider: `openai-api-key` present → `configured`; absent → `unknown`.
- **MUST NOT**: the agent never hashes a credential into the report,
  never emits a truncated form, never passes a fingerprint — the wire
  schema contains no credential-shaped field at all (gate 1 §4.1;
  gate 2 §4.3).
- **MUST**: the probe leg stays anonymous: the agent never accepts,
  holds, or requests any credential for discovery purposes; the fleet
  never invents a master «discovery key» (gate 2 §1 H3).

### 3.6 Caps and shrink-to-fit

- **MUST**: the fact caps — `provider` ≤ 60 chars; `models[]` sorted,
  ≤ 50 per row; `installations[]` ≤ 64 rows; the whole `models` object
  ≤ 16 KiB marshaled (AGW-25; gate 1 §2.1).
- **MUST**: the object shrinks to fit BEFORE send (rows halve; the
  terminal always-fits answer — an object with empty `installations`
  and the `notes`) — an over-cap send is impossible by construction
  (AGW-25).
- **MUST**: the per-config-file read cap — a hard 8 KiB; an oversize
  file or one unparsable within the cap = honest absence of the fact,
  never an error (AGW-25; gate 2 §2 item 3 — the v3 «8 KiB class»
  precedent).
- **MUST**: truncation rides the affected row's `note` («models
  truncated», «rows truncated») — no silent fact loss (AGW-25).
- A missing config, a dead probe port, absent marker fields — quiet
  zero (§2): an info fact, not an error, not a retry (AGW-25;
  gate 1 §2.3).

### 3.7 The probe leg: anonymous loopback

- **MUST**: the probe targets ONLY loopback (`127.0.0.1`, `::1`,
  `localhost`) — aiming it at external hosts is impossible by
  construction (AGW-25; gate 2 §1 H3).
- **MUST**: the targets are the fixed built-in port table: ollama 11434
  `GET /api/tags`; LM Studio 1234, llama.cpp server 8080, vLLM 8000 —
  `GET /v1/models` (AGW-25).
- **MUST**: one GET per server, 2 s timeout, no credentials — neither
  sent nor accepted (AGW-25; gate 2 §1 H3).
- **MUST**: only the documented response shapes are parsed:
  `{"models":[{"name":…}]}` (ollama) and `{"data":[{"id":…}]}` (the
  OpenAI-shape servers); everything else = absence of the fact (AGW-25).
- **MUST**: failure/dead port — quiet zero: an info fact, not an error,
  not a retry loop (AGW-25; gate 1 §2.3).
- **MUST NOT**: the probe never sends or accepts credential headers or
  parameters (§3.5; gate 2 §1 H3).

### 3.8 Leak discipline

- **MUST**: every emitted string (provider slug, model id, base_url,
  note) passes the names-only validator: the §3.6 length caps plus a
  credential-shape scan (token prefixes `sk-`/`ghp_`/`xox`-…, long hex
  or base64-ish runs, key-shaped assignments) (AGW-25).
- **MUST**: a credential-shaped string in an unexpected field drops the
  whole installation row BEFORE marshal (AGW-25).
- **MUST**: the drop is accompanied by a LOUD local log whose reason
  NEVER carries the offending value (mask-first: mask before truncate)
  (AGW-25).
- **MUST**: the agent emits NO events: the
  `models.credential_leak_suspected` incident detector is BOARD-side
  (ingest); the agent's only duties are the drop and the local log
  (AGW-25; gate 2 §1 H4).
- **MUST**: credential material is never read into memory for reporting
  and never emitted in any encoding (gate 1 §2.2; gate 2 §2 item 3,
  §4.1).

### 3.9 The `discovery_models` knob

- **MUST**: the leg is governed by the `discovery_models: auto|off`
  knob (default `auto`; unknown values refused at startup — the knob
  precedent) (AGW-25; PROTOCOL §7.1).
- **MUST**: `off` = the `models` field is absent entirely; `auto` and
  ran = the field is present, even with an empty `installations` (a real
  zero-and-ran) (AGW-25).
- This is the leg's only knob; the leg has no schedules, ports or
  credentials of its own (AGW-25).

### 3.10 Snapshot semantics and no-wipe

- **MUST**: the board's `models` mirror is a snapshot: the LAST report
  is stored; an identical re-report is a silent no-op (inherited
  verbatim from the §3 route semantics; gate 1 §2.3).
- **MUST**: absent ≠ empty: `models` absent = the leg did not report (an
  older agent / knob off) — the mirror is UNTOUCHED; `models` present
  with an empty `installations` = a real zero-and-ran — the mirror is
  WIPED. The no-wipe distinction carries over unchanged
  (gate 1 §2.3).
- **MUST**: no wire diffs; the board computes deltas against the
  previous snapshot (for growth SSE events) — the wire always carries
  the full snapshot (gate 1 §2.3).

### 3.11 Board ingest duties

- **MUST**: unknown `harness` attribution → the row dropped + audited
  (the `discovery.rejected` family); no dictionary ever auto-extends
  from a discovery report (gate 1 §2.4; the wave-3C precedent). The
  rule applies to both row classes identically, including
  `source: probe` rows (whose `harness` carries the probe source's
  slug, §3.2) — the mirror wave MUST decide the dictionary membership
  of probe slugs consciously, not by a silent carve-out.
- **MUST**: an unknown `exec_env` value → the row dropped + audited —
  the surface vocabulary is closed (gate 1 §2.4).
- **MUST**: unknown `provider` names are stored as advisory facts
  (OQ-3: no provider dictionary on this draft; duplicates are not
  feared — dedup by (provider, base_url)) (gate 1 §2.4, §5 OQ-3).
- **MUST**: a credential-shaped string in any unexpected `models` field
  = drop + the `models.credential_leak_suspected` incident-shaped audit
  event — it is incident data, not data (gate 1 §2.4; gate 2 §1 H4).
- **MUST**: the board enforces the §3.6 caps by the honest-422 family:
  a nameless row or an over-cap object → `422`, never a silent trim —
  the counters remain the agent's own honest report (gate 1 §2.1; §4).
- **MUST**: an authenticated report ticks `last_seen` as today (§3.1).

## 4. Error codes

The registry of route outcomes that matter for the `models` field.
Base — the deployed route semantics (vesma-eyes 1.38.0, §3 of
PROTOCOL.md); the field caps added by gate 1 §2.1. The agent's reaction
per outcome — third column.

| Code | Meaning | Source | Consumer reaction |
|---|---|---|---|
| `200` | report accepted; `last_seen` ticked | board | normal cycle; an identical re-report — silent no-op (§3.10) |
| `401` | executor token missing/invalid | board | retry in the normal cycle; no higher than info |
| `403` | URL id ≠ token identity, or the executor is revoked | board | do not retry as forever-4xx: identity is a configuration error; revoked is the kill-switch — presence must decay |
| `404` | no route (a pre-1.38 board) | board | 404-silence: nothing above info (§3.1) |
| `422` | validation: `harnesses` > 32; the `models` object over 16 KiB marshaled; `installations[]` > 64; a row without `provider` or with `models[]` > 50; an unknown form enum value | board | honest rejection, never a silent trim (gate 1 §2.1); the agent must be unable to send over-cap (shrink-to-fit §3.6) — an over-cap 422 is an agent defect |
| `429` | rate (the 60/60 s budget, shared with heartbeat) | board | retry on the next cycle beat; never fatal |

The board's audit/incident events (not HTTP codes, listed for
completeness):

| Event | Meaning | Source |
|---|---|---|
| `discovery.rejected` | a row with an unknown `harness` or `exec_env` dropped | board, ingest (§3.11) |
| `models.credential_leak_suspected` | a credential-shaped string in an unexpected `models` field — drop + incident | board, ingest (§3.11); the agent does NOT emit it (§3.8) |

## 5. Examples

The minimum example is a merge gate (ADR-0001 §1). The files live in
`examples/` next to the spec; examples carry only placeholders and
public documented endpoints — no real tokens, owner-machine paths or
hostnames (ADR-0001 §6).

| File | What it shows |
|---|---|
| `examples/config-source-installation.json` | a report with one `config` row (codex): openrouter via `model_providers`, `auth: configured` from a non-empty `env_key`, `notes.default_model` |
| `examples/probe-source-installation.json` | a report with one `probe` row: a local ollama answered `GET /api/tags` on 11434, `auth: anonymous`, `exec_env: metal` |
| `examples/credential-redaction.json` | `base_url` normalization before/after: query+fragment stripped; a credential-shaped query parameter → host-only; a credential string in an unexpected field → the row dropped, never hit the wire |

## 6. Conformance

The suite — `conformance/cases.skeleton.yaml`; the integrator's human
checklist — `conformance/checklist.md`. Executed by the
`tools/conformance` runner (stdlib + `jsonschema`; validates
declarations only — ADR-0001 §4). **Execution status — honestly:** the
runner is a single component-manifest vocabulary profile, so the
skeleton lives under the name `cases.skeleton.yaml` (the `run.py --all`
CI gate stays green); executing this vocabulary is a runner-profile
wave (a `tools/` change — through TL review). The machine JSON-Schema
of the `models` form lands with the board mirror (§9). The check
vocabulary and the targets (`examples/`,
`conformance/fixtures/invalid/`) are fixed; a green MUST-pass of the
suite once the runner-profile lands = the integration gate for the
agent and the board under this contract.

The check vocabulary (executor — a future runner profile):

| Check | What it does |
|---|---|
| `models_object_shape` | top-level `models` carries exactly `installations` (array) and MAY `notes` (object); a row — exactly the §3.2 fields, `note` MAY |
| `row_required_fields` | every row has `provider`, `base_url`, `auth`, `models`, `harness`, `exec_env`, `source` |
| `auth_enum` | `auth` ∈ `configured` \| `anonymous` \| `unknown` |
| `source_enum` | `source` ∈ `config` \| `probe` |
| `exec_env_metal_only` | `exec_env` = `"metal"` in this wave |
| `provider_length_cap` | `provider` ≤ 60 chars |
| `models_sorted_cap50` | `models[]` sorted and ≤ 50 items |
| `installations_cap64` | `installations[]` ≤ 64 rows |
| `base_url_normalized` | `base_url` = `scheme://authority[/base-path]`; no query/fragment/userinfo |
| `no_credential_material` | no string in the document passes the credential-shape scan (`sk-`/`ghp_`/`xox` prefixes, hex ≥ 40, base64 ≥ 40, key-shaped assignment) — the §3.8 names-only validator as a static check of examples. Value-scan exception (the CM `no_secret_in_vars` precedent): the explanatory document `credential-redaction.json` — its «before» lines intentionally show what gets redacted; only wire-shape documents are scanned |
| `harness_dictionary_spelling` | `source: config` rows carry the harness-dictionary spelling (codex, continue, claude-code, aider; zcode is absent from this build's table); `source: probe` rows carry the probe source's slug (§3.2) |
| `knob_values` | a knob declaration is only `auto` \| `off` (executor target — the agent's config declaration; the case lands with the board mirror) |

Cases: positive — the §5 wire examples
(`examples/config-source-installation.json`,
`examples/probe-source-installation.json`; `expect: pass`, all
`severity: must`; the explanatory `credential-redaction.json` is
outside the cases, see the exception above); negative — the
`conformance/fixtures/invalid/` fixtures (`expect: fail`).

## 7. Compatibility

- **SemVer**: `0.1.0-draft`; stable ratification — the first conformant
  implementation of BOTH legs (§9). A breaking change = MAJOR + a
  `max(90 days, 2 minor releases)` window with dual support
  (ADR-0001 §2); for pre-1.0 versions the window is 14 days.
- **Additivity — the unknown-field rule** (inherited from §5 of
  PROTOCOL.md, confirmed by AGW-25): unknown JSON fields are additive
  and ignored; a board ignoring `models` is conformant; an older agent
  that does not know `models` is conformant (the field is simply
  absent).
- **REMOVING a named field is a protocol MAJOR**: deleting any field of
  the §3.2 row or the top-level `notes` is breaking. Tightening a cap
  downward is breaking (it narrows what is allowed); upward — minor.
- **Layout-table extension** (a new harness, new read fields) — a minor
  contract change with committee notification; extending the
  `auth`/`source` vocabularies — MAJOR (closed enums).
- **Numbering**: the contract introduces no protocol number of its own —
  the legs' amendments are numbered by the vesma-agent AGW registry
  (AGW-25 — this wave); the contract owns the wire form, not the
  agent's amendment journal.
- **Consumers**: the agent writes the field per §3; the board ingests
  per §3.11 and serves the mirror/roster per the `GET /api/models`
  contract (`ModelsDiscoveredItem`, vesma-eyes — the `discovered`
  zone, see §9); the FE rendering — gate 3 (ux-blueprint MF1/MF2).

## 8. Threat model (mini-STRIDE)

The contract's asset — **the absence of credential material on the
wire**. Boundaries: (a) harness configs ↔ the agent's reader;
(b) agent ↔ board (the authenticated POST); (c) board ingest ↔
mirror/roster. The names-only discipline is the central control; every
mitigation below points at a §3 MUST or is marked «operational
control».

| Category | Threat | Mitigation | Verification |
|---|---|---|---|
| **I**nformation Disclosure | credential material from a config leaks into the payload (an `apiKey`/`env_key` value, a token in the query) | marker fields are never read into memory for reporting — only PRESENCE → `auth` (§3.5); a credential in the query → host-only/omit (§3.4); the 8 KiB read cap narrows the read surface (§3.6) | `no_credential_material`, `base_url_normalized` |
| **I**nformation Disclosure | the agent lured into «read everything, find model-looking strings» | the JSON-pointer-level layout table; scan heuristics forbidden (§3.3) | `models_object_shape` + table review (operational control) |
| **I**nformation Disclosure | a credential-shaped string slipped into a free field (`note`) | the names-only validator before marshal: drops the WHOLE row, loud local log with the value suppressed (§3.8) | `no_credential_material`; the board detector `models.credential_leak_suspected` (§3.11) — second line |
| **I**nformation Disclosure | a credential in the URL (`user:pass@host`, `?key=`) | userinfo/query/fragment always stripped; unparsable — omit, never guess (§3.4) | `base_url_normalized` |
| **S**poofing | a foreign executor reports under someone else's id | the route's executor-token class + identity-match: id ≠ token → 403 (§3.1, inherited) | route integration tests (operational control) |
| **E**levation of Privilege | a discovery fact grants itself authority: routing, allowlists, credential records | advisory, never authority: the field creates no rows, extends no dictionaries or allowlists (§3.1, §3.11) | board conformance (drop+audit tests, operational control) |
| **D**enial of Service | a bloated report chokes the board | the agent's shrink-to-fit (§3.6) — an over-cap send is impossible; honest-422 board caps (§4); hourly cadence without its own timer (§3.1) | `installations_cap64`, `models_sorted_cap50` |
| **D**enial of Service | the probe leg as an SSRF cannon or scanner | loopback-only, fixed port table, one GET, 2 s, no credentials, quiet zero without retries (§3.7) — aiming at an arbitrary host is impossible by construction | `exec_env_metal_only` + port-table review (operational control) |
| **R**epudiation | «who dropped the row / who sent a credential?» | drops audited (`discovery.rejected`), incidents named (`models.credential_leak_suspected`), the agent's local log loud (§3.8, §3.11) | operational control (the board's audit trail) |
| **T**ampering | dictionaries (`exec_env`, harnesses) rewritten through a report | unknown values drop+audit, closed vocabularies, growth is an owner act (§3.11) | operational control |

Conscious residual risks (outside the contract): a harness process
reads its OWN owner-configured credentials — that is the harness's
threat model, not the fleet's (gate 2 §6); full board-host compromise —
outside the agent wire; mirror abuse after ingest — the domain of the
roster and grant contracts (gate 2).

## 9. Migration and implementation status

There is no legacy: the field is introduced for the first time. The
legs' implementation status — honestly:

| Leg | Status | Where it lives |
|---|---|---|
| Agent (field writer) | **merged** — protocol amendment AGW-25 «discovery v6», 2026-10-28 | vesmaro/vesma-agent, the main (merge b98960e) branch; the norm — `docs/PROTOCOL.md` §3 (addendum) + §7.1 (knob) |
| Board mirror (ingest into `GET /api/models`) | **not merged** — the next vesma-eyes wave | the ingest target schema is already served by the board: `ModelsDiscoveredItem` in `ModelsRosterOut.discovered` (the «discovered» zone, the MF2 cut) — the field exists so the FE contract is stable when the discovery leg lands; the zone stays honestly empty while no `models` slice rides the wire |
| Roster UX (mirror rendering) | ratified by gate 3 | `ux-blueprint.md` MF1 «Ростер» (cb166a8), `GET /api/models` — the single aggregation point (OQ-1) |

Input order: (1) the agent leg — done (AGW-25); boards without the
mirror stay conformant — the field is additive and ignored (§3.1, §7);
(2) the board mirror — ingest per §3.11, no-wipe semantics §3.10,
honest 422 §4; (3) stable ratification — both legs' conformance green.
Intermediate states (the mirror exists, the field does not travel; the
field travels, no mirror) — allowed and honest: both sides read/write
additively.

The implementation MUST NOT depend on the wave order: the agent does
not wait for the mirror, the mirror does not wait for the UX — the
«who breaks whom» dependency is absent by the additivity construction.

## 10. References

- `docs/PROTOCOL.md` §3 (the «Models-fleet addendum — discovery v6»
  addendum, AGW-25, 2026-10-28) and §7.1 (`discovery_models`) — the
  normative source of the agent leg; vesmaro/vesma-agent, the
  main (merge b98960e) branch.
- Gate 1 — `docs/design/models-fleet/discovery-contract-draft.md`
  (vesmaro/vesma-eyes, the `feat/models-fleet-blueprint` branch,
  daf969b): wire shape §2, red lines §2.2, trust boundaries §4.
- Gate 2 — `docs/design/models-fleet/security-verdict.md` (same,
  832cd7a): the OQ-4 verdict with amendments 1–2 §2, the final red
  lines §4, the H1–H4 verdicts §1.
- Gate 3 — `docs/design/models-fleet/ux-blueprint.md` (same, cb166a8):
  MF1/MF2 — the mirror consumers.
- `specs/decision-provider/v1` — the «decision provider» family; not to
  be confused with a models-fleet provider (§2, the glossary).
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — the
  layer's structure and governance; the contract's form.
- [ADR-0002](../../../adrs/0002-agent-discovery-contract.md) — the
  codification decision (the authority trail).
- [Glossary](../../../GLOSSARY.md), the
  [ecosystem map](../../../ECOSYSTEM.md).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword
  interpretation.
