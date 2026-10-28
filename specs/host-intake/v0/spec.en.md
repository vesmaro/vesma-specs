---
contract: host-intake
version: 0.1.0-draft
status: draft
decisions: [ADR-0001, ADR-0002, "owner directive 2026-10-28 (two clauses: per-harness models re-key + the explicit collection-surface contract)", "the agent-side contract draft — docs/design/host-intake-contract-draft.md (vesmaro/vesma-agent, the feat/host-intake-contract branch); the draft's gates are owner-approved (FC-6+FC-7 this wave; FC-8/9 — DEFERRED to v2; the loopback probe approved; dual-form emission approved)", "gates carried: fleet security-verdict (vesma-eyes, feat/models-fleet-blueprint, 832cd7a) — the red lines", "the AGW-25/AGW-26 lineage (discovery v6 → v7 re-key)"]
ratified: |-
  Not ratified (draft). Authority trail: owner directive 2026-10-28 —
  two clauses (per-harness models re-key; the explicit collection
  surface as the trust/transparency surface); the agent-side contract
  draft (docs/design/host-intake-contract-draft.md, vesmaro/vesma-agent,
  feat/host-intake-contract) is the source of the catalog, principles,
  the per-harness table and the disciplines; its gate decisions are
  owner-approved (FC-6+FC-7 this wave, FC-8/9 deferred to v2, the
  loopback probe approved, dual-form emission approved); the config-read
  red lines carry over from the ratified security-verdict (832cd7a,
  models-fleet gate 2); the protocol lineage is AGW-25 (discovery v6,
  merged) → AGW-26 (v7 re-key, the feat/host-intake-contract branch).
  Stable ratification — the first conformant implementation of the
  catalog legs by the agent (v7) and a green conformance run.
language: en (informative mirror)
---

# host-intake v0 — the explicit host-collection catalog contract

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian
> text prevails. The mirror is maintained in the same change as the
> Russian text (single-commit sync policy).
>
> **Status: draft (0.1.0-draft).** The contract fixes the COMPLETE
> explicit catalog of what the outbound ЦУП agent (`vesmaro-agent`)
> collects on a host — the fleet's trust and transparency surface
> (clause 2 of the owner directive 2026-10-28) — and normatively defines
> two new/re-keyed legs: FC-6 (models per-harness — the re-key
> superseding the v6 standalone table of AGW-25) and FC-7 (mcp_servers).
> Anything not named in the catalog of §3.2 is not collected. Form
> changes after ratification go through the SemVer process only
> (ADR-0001 §2).

The key words MUST / MUST NOT / SHOULD / MAY are interpreted per
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Prose is English;
identifiers, fields and enum values are EN. Every requirement traces to
the agent-side contract draft («contract §…» =
`docs/design/host-intake-contract-draft.md`, its gates owner-approved on
2026-10-28), the carried security-verdict («gate 2», 832cd7a), or the
AGW-25/AGW-26 protocol lineage; the text marks them. Budgets marked
«(brief 2026-10-28)» are spec-phase wave budgets laid over the approved
gates (listed in §10).

## 1. Scope

The contract fixes the **explicit collection catalog** — the complete
list of fact classes (FC) the agent may gather on a host, with the
surface principles (P1–P6), the normative wire forms of the new/re-keyed
legs (FC-6, FC-7), and the never-collected boundary. The trust
principle: **the owner can see the complete "what agents collect" list**
— the catalog is public, versioned and diffable per release; every wire
field of the report maps to exactly one FC id (§3.6).

**In scope:**

- the collection-surface principles P1–P6 (§3.1);
- the fact-class catalog FC-1…FC-9 with statuses and caps (§3.2);
- the never-collected boundary — verbatim (§3.5);
- FC-6 — models per-harness: structural attribution to DISCOVERED
  harnesses, the built-in per-harness layout table, the documented
  provider string forms, the anonymous loopback probe (the fixed table +
  harness-configured loopback base_urls), caps, the carried v6 red lines
  (§3.3);
- FC-7 — mcp_servers per harness: names + transport kind from
  documented caches/configs, the wire form, caps (§3.4);
- the board's transparency surface: rendering "what agents collect"
  FROM this contract, per agent version; the field → FC map (§3.6);
- the honest implementation status (§9).

**Out of scope (neighbouring domains):**

- FC-8 (tooling) and FC-9 (compute envelope) — **catalogued, status
  DEFERRED: v2** — the owner's decision recorded at the draft gate;
  implementation is a separate v2 class wave (§3.2);
- the wire discipline of the EXISTING `models` field (the row form,
  `base_url` normalization, snapshot/no-wipe, board ingest duties) — the
  norm of [agent-discovery](../../agent-discovery/v0/spec.md) v0; this
  contract re-litigates only the row-POPULATION rules (the per-harness
  re-key) and adds the `base_url`-optional extension for endpoint-less
  sources (§3.3);
- the discovery report's `sessions[]` — **outside the agent's collection
  surface**: the field exists on the wire but is fed by the board's
  eyes-side scanner, not the agent (verified 2026-10-28, see §9); this
  contract catalogues it as "not an agent fact" (§3.2, the §3.6 map);
- credential storage, sharing grants, the pull proxy — gate 2's verdict
  (H1/H2); roster UX — gate 3; the MANAGED allowlist and the shim wave —
  separate, untouched surfaces (contract §2);
- the board mirror wave (ingest of the new fields) — a separate
  vesma-eyes decision (contract §9).

**Consumers:** the `vesmaro-agent` agent (catalog compliance), the
`vesma-eyes` board (rendering "what agents collect" from the contract;
ingest of the additive fields), the owner (trust-surface audit),
third-party agent integrators, the layer's conformance runner.

## 2. Terminology

The terms **discovery (agent → board)**, **provider (fleet)**, **model
(fleet)**, **installation (model)**, **harness**, **quiet zero**,
**shrink-to-fit** are defined in the
[glossary](../../../GLOSSARY.md) and
[agent-discovery §2](../../agent-discovery/v0/spec.md) and are not
redefined here. Contract-local terms:

| Term | Meaning |
|---|---|
| fact class (FC) | A catalog class: one unit of the "what the agent collects" surface. Each FC carries: what is collected, the host source, the emission form, caps, status (live / re-key / DEFERRED). The §3.2 catalog is a closed list; adding a class = a contract amendment with an owner gate (P1). |
| per-harness attribution | The structural rule of FC-6/FC-7: a fact row may carry only such a `harness` as the agent ACTUALLY discovered on this host via the inventory (FC-1/FC-2). The models/MCP scan runs OVER the inventory results — a row for an undiscovered harness is impossible by construction (contract §3.1). |
| never collected | The catalog's verbatim boundary: file contents (outside the named per-class exceptions), project/workspace names, prompts and session content, environment-variable VALUES, network traffic, credential material in any form (§3.5). |
| transparency surface | The board's rendering of "what agents collect" FROM this contract, per agent version: one card per FC id (what, why, caps, privacy line); built via the contract↔agent version handshake (§3.6; contract §7). |
| harness bucket | The FC-6 provider attribution when NO documented string form parses: provider = the harness slug; the reason is a local-log fact, never the wire; an advisory name board-side (§3.3.3). Provider guessing is forbidden (contract §3.2; draft gate OQ-3: never guess). |
| dual-form emission | The OQ-3-approved emission form of FC-6: `models[]` carries the RAW frontmatter/config strings verbatim; the parsed provider rides the row's `provider` field — and only when the documented form parses (§3.3.3). |
| DEFERRED (v2) | A catalog-class status: the class is described (what, source, caps), implementation deferred by the owner's decision to the v2 class wave; the agent does NOT collect it until activation (§3.2, §9). |

## 3. Contract

### 3.1 Collection-surface principles (P1–P6)

- **P1 — Explicit surface.** The §3.2 catalog is the COMPLETE list of
  what is collected. Anything not named is not collected. **MUST**: the
  agent collects only the catalog-named classes. Adding a class is a
  contract amendment with an owner gate (contract §1 P1).
- **P2 — Names and enums, never contents.** The v3 discipline
  generalized: file contents never leave the machine; every bounded
  content-read exception is named per class and emits names, booleans or
  enum facts. **MUST NOT**: "looks-like-a-model" scanning — ever
  (contract §1 P2; gate 2 §2 amendment 1 — the layout-table precedent).
- **P3 — Credential material never.** Key/token/secret VALUES are never
  read for reporting, never held in retained structures, never emitted
  in any encoding. Credentials appear only as PRESENCE markers
  (`auth: configured | anonymous | unknown`) at fields/files the
  built-in table names. **MUST** (contract §1 P3; gate 2 §2 item 3,
  §4.1).
- **P4 — Honest absence.** An absent, undocumented or unparsable
  surface is an empty fact (quiet zero), never an error, never a guess.
  "Not determinable" rows are omitted from the table, not invented.
  **MUST** (contract §1 P4).
- **P5 — Additive and versioned.** Fact classes carry since-versions;
  the wire stays additive (the unknown-field rule, 404-silence —
  unchanged). **MUST** (contract §1 P5; agent-discovery §3.1, §7).
- **P6 — Transparency surface.** The board renders "what agents
  collect" FROM this contract, per agent version: every wire field maps
  to an FC id (§3.6). No new leg — the contract text ships with the
  agent (docs pinned at build; the version handshake exposes the pair).
  **MUST** (contract §1 P6, §7).

### 3.2 The fact-class catalog

A closed list (P1). Status column: `live (vN)` — the leg has ridden the
wire since agent-protocol version N (`docs/PROTOCOL.md` §3, the
vesma-agent AGW registry); `re-key (v7)` — the population rules switch
in this wave (AGW-26); `DEFERRED (v2)` — catalogued, implementation
deferred by the owner (draft gate).

| id | Class | What the agent collects | Source | Emission | Caps | Status |
|---|---|---|---|---|---|---|
| FC-1 | `harnesses[]` | Known CLI harnesses on PATH: name, version, path | exec.LookPath + discovery_extra | names/versions/paths | 32 rows | live (v1) |
| FC-2 | `environments[]` | Harness homes from the built-in fingerprint table: kind, markers, session_hints (store name + count), exec_env merge | stat/glob over discovery_roots | facts, no contents | 8 KiB/env | live (v2+v4) |
| FC-3 | `environments[].capabilities` | Names-only harness inventory: specialists, skills, plugins, instructions + counts + booleans | dir walks + 2 named content reads (pi `packages[]`, the zcode gcw marker) | names/counts/booleans | 50/50/30/30, 8 KiB | live (v3) |
| FC-4 | `distrobox_containers` | Per-container honest verdicts; exec_env merge identity | distrobox list/probe (read-only) | facts | 30 s leg | live (v4) |
| FC-5 | `runtime`, `k8s_nodes/pods/verdicts` | Runtime-surface honesty; content-free cluster lists | multi-signal detect; stdlib REST | facts | 30 s leg | live (v5) |
| FC-6 | `models` per-harness | Per DISCOVERED harness: configured providers (name, base_url normalized, auth enum), available models (what the config/catalog names + anonymous local-server availability), default model | the §3.3.2 per-harness layout table | names/enums/normalized URLs | 64 rows, 50/row, 16 KiB, 8 KiB/file | **re-key (v7, AGW-26)** — supersedes the v6 standalone table |
| FC-7 | `mcp_servers` per harness | MCP/extension server NAMES + transport kind | documented caches/configs (pi `mcp-cache.json`; zcode/copilot mcp sections where documented) | names/kinds only — never argv, env, URLs | ≤30 names/harness, 8 KiB | **approved (v7)** — new |
| FC-8 | tooling | Presence + version of a FIXED built-in host-tool list (git, podman, docker, python3, node, go, …) | LookPath + one `--version` line | names/versions | ≤40 tools, 4096-char read cap | **DEFERRED (v2)** |
| FC-9 | compute envelope | CPU cores, RAM total, disk free on the state volume, GPU presence (name string only) | /proc + statvfs + `nvidia-smi -L` (name string) | hardware facts | one-shot per pass | **DEFERRED (v2)** |

**MUST**: FC-8 and FC-9 are NOT collected until the v2 wave activates
them — cataloguing ≠ activation (draft gate; contract §2 PROPOSED rows →
the owner's "deferred" decision). **MUST**: the status column changes
only through a contract amendment (P5).

**The field → FC map** (complete; the basis of the §3.6 rendering):

| Discovery-report field | FC |
|---|---|
| `harnesses[]` | FC-1 |
| `environments[]` | FC-2 |
| `environments[].capabilities` | FC-3 |
| `distrobox_containers` | FC-4 |
| `runtime`, `k8s_nodes`, `k8s_pods`, `k8s_verdicts` | FC-5 |
| `models` | FC-6 |
| `mcp_servers` (since v7) | FC-7 |
| `sessions[]` | **NOT the agent** — the board's eyes-side scanner (see §9) |

### 3.3 FC-6 — models per-harness (the re-keyed core)

#### 3.3.1 Attribution (structural)

- **MUST**: an installation row carries `harness` = a name the inventory
  (FC-1/FC-2) ACTUALLY discovered on this host; the board dictionary
  decides admission, as ever. The models scan runs OVER the inventory
  results — a model row for an undiscovered harness is impossible by
  construction (contract §3.1).
- **MUST**: the v6 standalone table (codex/continue/claude-code/aider as
  a detached config set) is SUPERSEDED: its rows are NOT deleted — they
  fold into the §3.3.2 per-harness table as the rows of those harnesses;
  the table becomes ATTACHED to the fingerprint inventory — one built-in
  registry with per-harness sections (contract §0).

#### 3.3.2 The per-harness layout table (built-in, typed decodes, the v3 discipline)

| harness | source | fields named by the table | credential marker (presence only) | grounded |
|---|---|---|---|---|
| zcode | `~/.zcode/agents/*.md` frontmatter (frontmatter-first read; ≤64 files, 8 KiB/file — brief 2026-10-28) | `model:` (scalar or list — try-in-order), `tier:`, agent `name:` (provider from the documented string forms: the `(provider)` suffix, the `provider/model` prefix; display-name and qualified id are both legal) | — (tier arrays carry provider slugs) | 2026-10-28: the GCW installer renders the fleet `models.yaml` into these files; live ids documented (`ollama-cloud/glm-5.3-flash`, `z/glm-5.3`) (contract §3.2) |
| copilot | `~/.copilot/agents/*.agent.md` frontmatter (same budgets) | the same `model:`/`tier:` fields; the `" (copilot)"` suffix convention | — | 2026-10-28: `model: GLM 5.3 Flash (ollama-cloud)`, `tier: 1` verified live; GitHub-side model catalogs are server-only — the LOCAL fact is what the definitions name (the server-only honesty lives in this description/the catalog, not on the wire row) (contract §3.2) |
| codex | `~/.codex/config.toml` | top-level `model`, `model_provider`; `model_providers.<name>.{name, base_url, env_key}` | `env_key` non-empty → configured | v6, carried (contract §3.2; AGW-25) |
| continue | `~/.continue/config.json` | `models[].{provider, model, apiBase, apiKey}` | the `apiKey` field present → configured | v6, carried (AGW-25) |
| claude-code | `~/.claude/settings.json` | `model`; from `env` — only KEY NAMES with the `ANTHROPIC_` prefix | any `ANTHROPIC_*` name → configured; none → unknown | v6, carried (contract §3.2; AGW-25) |
| aider | `~/.aider.conf.yml` | `model`, `openai-api-base`, `openai-api-key` | `openai-api-key` present → configured; absent → unknown | v6, carried (AGW-25) |
| pi | `<home>/.pi/agent/` | no documented model catalog today → honest absence (model rows: none); `auth.json` EXISTENCE → the pi auth fact | `auth.json` exists → configured (the value is NEVER read); no file → unknown | 2026-10-28: `auth.json` present on core-51's pi (contract §3.2); emission: one provider `pi` row, the `models` field omitted (omitempty; an empty list would be a zero-and-ran claim — the key is not emitted) (brief 2026-10-28) |

- **MUST**: the table is built-in and versioned in the agent; reads go
  ONLY through the named fields at JSON-pointer/section-path level;
  parse-and-scan heuristics are forbidden (gate 2 §2 amendment 1 —
  carried; contract §3.2).
- **MUST**: gemini and qwen have NO rows: neither the v6 table (AGW-25)
  nor the draft's grounded set names them (brief 2026-10-28: absent; the
  draft §3.2 row's «continue / aider / gemini / qwen — as v6 rows»
  mention is superseded — the v6 table had no such rows).
- **MUST**: pi with `auth.json` absent emits `auth: unknown`, not
  `anonymous` — the v6 family precedent (claude-code/aider,
  agent-discovery §3.5): the absence of a marker does not prove
  anonymity — the credential may live in an env var or an OS store this
  build never reads.
- **MUST**: a file over the 8 KiB read cap, non-regular or unparsable
  within the cap = an honest row absence, never an error (contract
  §3.4; P4).
- **MUST**: the default model — ONLY from the pointers the table names:
  codex top-level `model` → a per-row note ("default model from harness
  settings"). **MUST NOT**: a default fact on frontmatter rows
  (zcode/copilot): `model:`/`tier:` are decoded but NEVER interpreted —
  models are per-agent (lists in every agent definition), a single
  per-harness default would be a guess (reconciled with the landed
  AGW-26 implementation, 2026-10-28). The wire form — the per-row note
  (the spec-phase resolution under the approved OQ-5: "default model of
  harness `<slug>`" rides the `note` of the row whose `models[]`
  contains the default string; the top-level `notes` MAY be omitted —
  the field is omitempty already in agent-discovery §3.2, and a global
  `default_model` scalar is not an honest per-harness fact).
- **MUST**: a row's `base_url` MAY be absent (omitempty) for sources
  that name no endpoint (the zcode/copilot frontmatter rows; the pi row)
  — honest absence, URL guessing forbidden (P4; an additive extension of
  the agent-discovery §3.2 row form: optional in the new sources, the
  required fields of the others untouched).

#### 3.3.3 The documented provider string forms (dual-form emission, never guess)

The documented string forms of frontmatter/config model rows (contract
§3.2; draft gate OQ-3 approved):

- **MUST**: form 1 — the `(provider)` suffix: `Model Name
  (provider-slug)` → provider = the slug; the raw string rides
  `models[]` verbatim.
- **MUST**: form 2 — the `provider/model` prefix: a qualified id
  (`ollama-cloud/glm-5.3-flash`) → provider = the prefix, model id = the
  rest.
- **MUST**: form 3 — the literal vendor form `(copilot)`: the
  ` (copilot)` suffix → provider = `copilot`; the GitHub-side catalog is
  server-only — `base_url` is NEVER synthesized (honest absence); the
  server-only honesty lives in the layout-table description and the
  catalog, NOT on the wire row — frontmatter rows carry no note (P4: a
  note the code cannot fill must not be promised).
- **MUST**: no documented form parsed → the harness bucket: provider =
  the harness slug; the reason ("no documented provider form") is a
  LOCAL-LOG fact, never the wire; an advisory name board-side
  (agent-discovery §3.11). **MUST NOT**: provider guessing,
  display-name → id conversion, any "looks-like-a-provider" heuristics.
- **MUST**: dual-form emission — `models[]` carries the RAW strings
  verbatim (sorted, ≤50); the parsed provider rides the row's
  `provider`; both facts in one row (OQ-3 gate: raw string + parsed pair
  only when the documented form parses).
- **MUST**: `model:` scalar OR list — try-in-order (contract §3.2).

#### 3.3.4 The probe leg: anonymous loopback (the fixed table + harness-configured base_urls)

- **MUST**: the fixed v6 loopback-server table stands unchanged: ollama
  11434 `GET /api/tags`; LM Studio 1234, llama.cpp server 8080, vLLM
  8000 — `GET /v1/models`; one GET per server, 2 s timeout, no
  credentials; only the documented response shapes parse
  (`{"models":[{"name":…}]}` ollama; `{"data":[{"id":…}]}` OpenAI-shape
  servers); failure/dead port — quiet zero (contract §3.3; AGW-25).
- **MUST** (the approved OQ-2 gate): a `base_url` configured BY a
  discovered harness that resolves LOOPBACK MAY be probed anonymously —
  one GET model-list, short timeout, quiet zero; the budget is ≤8 extra
  targets per pass (brief 2026-10-28); the purpose — availability facts
  for the local/self-hosted providers the harness actually uses
  (contract §3.3).
- **MUST NOT**: non-loopback endpoints are never dialed; endpoints with
  a credential marker (`auth: configured`) are never dialed — the agent
  has no key and must never acquire one (the H3 verdict of gate 2
  stands; contract §3.3).
- **MUST**: the probe client is zero-redirect (contract §3.4; carried).
- **MUST**: loopback only (`127.0.0.1`, `::1`, `localhost`) — aiming at
  an external host is impossible by construction (AGW-25; gate 2 §1 H3).

#### 3.3.5 Caps and shrink-to-fit

- **MUST**: `provider` ≤ 60 chars; `models[]` sorted ≤ 50 per row;
  `installations[]` ≤ 64 rows; the `models` object ≤ 16 KiB marshaled;
  the per-file read cap — a hard 8 KiB (contract §2 FC-6, §3.4; AGW-25).
- **MUST**: the zcode/copilot frontmatter-first read: ≤64 agent
  definition files per pass (brief 2026-10-28), each under the 8 KiB
  read cap.
- **MUST**: the object shrinks to fit BEFORE send (shrink-to-fit);
  truncation rides the affected row's `note`; an over-cap send is
  impossible by construction (AGW-25; contract §3.4).
- **MUST**: a missing config, a dead probe port, absent marker fields —
  quiet zero: an info fact, not an error, not a retry (P4; AGW-25).

#### 3.3.6 The v6 red lines — carried verbatim

The following AGW-25/gate 2 disciplines are re-litigated WITHOUT
CHANGES (contract §3.4 "carried verbatim"):

- **MUST**: the names-only validator — drop, never mangle: every
  emitted string (provider slug, model id, base_url, note) passes the
  length caps + the credential-shape scan.
- **MUST**: `base_url` normalization → `scheme://authority[/base-path]`;
  query/fragment are always stripped; userinfo is stripped; a
  credential-shaped query parameter (detected by the PRESENCE of the
  name) → host-only or omit — the value is never echoed.
- **MUST**: `auth` ∈ `configured | anonymous | unknown` — ONLY from the
  PRESENCE of the marker fields the table names; marker-field values are
  never read into the payload in any encoding.
- **MUST**: a credential-shaped string in an unexpected field → the WHOLE
  row dropped BEFORE marshal + a LOUD local log whose reason NEVER
  carries the value (mask-first: mask before truncate).
- **MUST**: the agent emits NO events — the
  `models.credential_leak_suspected` incident detector is BOARD-side
  (ingest); the agent's duties are the drop and the local log.
- **MUST**: credential material is never read into memory for reporting
  and never emitted in any encoding (P3; gate 2 §2 item 3, §4.1).
- **MUST**: `exec_env` — only `"metal"` in this wave; container config
  surfaces ride the follow-up wave (contract §3.4).

### 3.4 FC-7 — mcp_servers per harness (normative)

- **MUST**: the wire is an additive top-level member of the field family
  (the capabilities/FC-3 precedent), next to `models`:

```json
{"mcp_servers": [{"harness": "pi", "exec_env": "metal",
  "servers": ["context7", "playwright"],
  "count": 5}]}
```

- **MUST**: the element = `{harness, exec_env, servers[], count}`;
  structural attribution (§3.3.1): `harness` — a discovered harness
  only; `exec_env` — only `"metal"` in this wave.
- **MUST**: `servers[]` — sorted names ≤30 per harness (contract §4);
  **MUST**: `count` — the FULL total of names found, even when
  `servers[]` is truncated at 30 (an honest counter; brief 2026-10-28).
- **MUST**: the sources — documented caches/configs ONLY, typed decodes:
  pi `~/.pi/agent/mcp-cache.json` — the `servers` field is a DICT: the
  server names are ONLY the dict KEYS of that map; the cache VALUES are
  never decoded (the landed AGW-26 shape; the contract draft's list
  wording `{version, servers[]}` was wrong and is being fixed on the
  agent-repo side); zcode/copilot mcp sections — where documented
  (contract §4).
- **MUST NOT**: argv, env, URLs and any cache/config values are never
  decoded or emitted — names and transport kind only (contract §2 FC-7,
  §4).
- **MUST**: the transport kind (`stdio`/`http`), when the documented
  source names it, rides an optional `transports` map
  (`{name: kind}`, omitempty) on the element; the encoding form is a
  spec-phase decision under the approved FC-7 gate (contract §4 collects
  names + kind; the brief's literal wire names `servers ≤30 sorted`).
- **MUST**: honest absence elsewhere: no documented cache/section → the
  harness element is absent (the field family's zero-and-ran);
  undocumented sources are NOT scanned (P2, P4).
- **MUST**: FC-7 is governed by the same `discovery_models: auto|off`
  knob (default `auto`); `off` = both the `models` and `mcp_servers`
  fields absent entirely (brief 2026-10-28; the knob precedent,
  agent-discovery §3.9).
- **MUST**: the family cap — 8 KiB per element (contract §4); on
  truncation the `count` stays full and the truncation is carried by the
  honest counter (the row above).
- Board ingest duties are inherited from the
  [agent-discovery §3.11](../../agent-discovery/v0/spec.md) family: unknown
  `harness`/`exec_env` → drop + audit; an over-cap object → an honest
  422.

### 3.5 Never collected (the verbatim boundary)

**Never collected** (contract §2, verbatim): file contents (outside the
named per-class exceptions), project/workspace names, prompts and
session content, environment-variable VALUES, network traffic,
credential material in any form. The MANAGED allowlist and the shim wave
are separate surfaces this contract does not touch.

- **MUST NOT**: no catalog class reads or emits anything from the list;
  a conflict between the catalog and this boundary resolves in favour of
  the boundary until clarified (the P2, P3 lexicon).

### 3.6 The transparency surface (the P6 deliverable)

- **MUST**: this contract's text is pinned into the agent (docs + a
  build-time contract-version stamp exposed through the version
  handshake) — the "agent version ↔ contract version" pair is observable
  (contract §7).
- **MUST**: the board renders the static "what agents collect" view FROM
  the contract: one card per FC id — what, why, caps, privacy line; the
  rendering is pinned to the contract version matching the agent version
  (contract §7).
- **MUST**: every payload field the agent ever sends maps to exactly one
  FC id (the §3.2 map); a field without an FC id is an implementation
  defect, not a new surface (P1).
- The complete collection list is public, versioned and diffable per
  release: the user-trust deliverable (contract §7).

## 4. Error codes

The contract introduces no new codes: the catalog legs (FC-6, FC-7) ride
the EXISTING `POST /api/executors/{executor_id}/discovery` route, and
the route-outcome registry is inherited from
[agent-discovery §4](../../agent-discovery/v0/spec.md) unchanged: `200`
(accepted, `last_seen` ticked), `401`/`403` (token/identity/revoked),
`404` (a pre-1.38 board → 404-silence), `422` (the family's honest cap
validation), `429` (the 60/60 s budget). The audit events —
`discovery.rejected` (unknown `harness`/`exec_env`) and
`models.credential_leak_suspected` (a board-side incident detector) —
are the same.

| Code | Application to this contract's fields |
|---|---|
| `422` | `models` over 16 KiB marshaled; `installations[]` > 64; `models[]` > 50; an `mcp_servers` element over 8 KiB; `servers[]` > 30; an unknown form enum value — honest rejection, never a silent trim (the agent's shrink-to-fit makes an over-cap send an agent defect) |
| `404` | the FC-6/FC-7 leg stays silent below info on a board without the route — additivity creates no schedule and no retries (§3.1 P5) |

## 5. Examples

The minimum example is a merge gate (ADR-0001 §1). The files live in
`examples/` next to the spec; placeholders and public documented
endpoints only — no real tokens, owner-machine paths or hostnames
(ADR-0001 §6).

| File | What it shows |
|---|---|
| `examples/zcode-frontmatter-installation.json` | a zcode row derived from frontmatter: `models[]` — raw strings verbatim (the display form and the qualified id), the provider parsed by the documented suffix form; `base_url` omitempty (the frontmatter names no endpoint); no default or note fact on a frontmatter row (§3.3.2, §3.3.3) |
| `examples/pi-auth-marker-row.json` | the pi auth-marker row: provider `pi`, the `models` field omitted (omitempty; no documented catalog — honest absence), `auth: configured` from the EXISTENCE of `auth.json` (the value never read) |
| `examples/mcp-servers-field.json` | the additive top-level `mcp_servers`: a pi element from `mcp-cache.json` — names only, sorted, `count` = the full total, the optional `transports` map |
| `examples/credential-redaction.json` | the discipline before/after: `base_url` normalization; a harness-configured loopback `base_url` WITHOUT a marker → an anonymous probe allowed; with a marker → never dialed; a credential string in an unexpected field → the row dropped before marshal |

## 6. Conformance

The suite — `conformance/cases.skeleton.yaml`; the integrator's human
checklist — `conformance/checklist.md`. Executed by the
`tools/conformance` runner (stdlib + `jsonschema`; validates
declarations only — ADR-0001 §4). **Execution status — honestly** (the
agent-discovery §6 precedent): the runner is a single
component-manifest vocabulary profile, so the skeleton lives under the
name `cases.skeleton.yaml` (the `run.py --all` CI gate stays green);
executing this vocabulary is a runner-profile wave (a `tools/` change —
through TL review). The machine JSON-Schema lands with the board mirror
wave of the new fields. A green MUST-pass of the suite once the
runner-profile lands = the agent's integration gate under this
contract.

The check vocabulary (executor — a future runner profile):

| Check | What it does |
|---|---|
| `models_field_shape` | top-level `models` carries `installations[]` rows of the agent-discovery §3.2 form; `base_url` omitempty ONLY for endpoint-less sources; the pi row MAY omit `models` (omitempty, §3.3.2) |
| `fc6_harness_attribution` | every row's `harness` — a discovered-harness dictionary spelling; no rows of undiscovered harnesses (§3.3.1) |
| `provider_parse_forms` | `provider` — a documented-form result (suffix/prefix/`copilot` vendor) or the harness bucket with a `note` reason; no guessed providers (§3.3.3) |
| `auth_enum` | `auth` ∈ `configured` \| `anonymous` \| `unknown`, derived from marker-field presence only (§3.3.6) |
| `base_url_normalized` | a present `base_url` = `scheme://authority[/base-path]`, no query/fragment/userinfo (§3.3.6) |
| `row_caps` | `provider` ≤ 60; `models[]` sorted ≤ 50; `installations[]` ≤ 64; truncation — in the `note` (§3.3.5) |
| `no_credential_material` | the §3.3.6 names-only validator as a static scan of wire-shape documents; the explanatory `credential-redaction.json` — outside the scan (the CM `no_secret_in_vars` / agent-discovery §6 precedent) |
| `mcp_servers_field_shape` | elements `{harness, exec_env, servers[], count}`; `count` — the full total; `exec_env` = `"metal"` (§3.4) |
| `mcp_names_cap30` | `servers[]` sorted ≤ 30 per harness (§3.4) |
| `mcp_names_only` | no argv/env/URL-shaped strings in `servers[]`/`transports` — names and kinds only (§3.4) |
| `knob_values` | a `discovery_models` knob declaration — only `auto` \| `off`; governs FC-6 and FC-7 jointly (§3.4) |

Cases: positive — the §5 wire examples (`examples/…`;
`expect: pass`, `severity: must`; the explanatory
`credential-redaction.json` — outside the cases); negative — the
`conformance/fixtures/invalid/` fixtures (`expect: fail`).

## 7. Compatibility

- **SemVer**: `0.1.0-draft`; stable ratification — the first conformant
  agent implementation (v7) and a green conformance run. A breaking
  change = MAJOR + a `max(90 days, 2 minor releases)` window with dual
  support; below 1.0 the window is 14 days (ADR-0001 §2).
- **Additivity**: FC-7 (`mcp_servers`) — a new additive top-level field:
  a board ignoring it stays conformant (the unknown-field rule); an
  older agent without the field stays conformant. The FC-6 re-key
  changes the POPULATION rules of the existing `models` field
  (per-harness attribution, frontmatter rows, `base_url` omitempty for
  endpoint-less sources) with the row form UNCHANGED: an old board reads
  the new rows as ordinary installations — additively (§3.1 P5;
  agent-discovery §7).
- **REMOVING a named field = MAJOR** (inherited); extending the
  per-harness table (a new harness, a new named field) — a minor change
  with committee notification; activating DEFERRED classes (FC-8/FC-9) —
  a minor change of THIS contract with an owner gate (P1: adding a
  collected class is always gated).
- **Consumers**: the agent — obeys the catalog and the §3.3/§3.4 forms;
  the board — ingest per the agent-discovery §3.11 family + the §3.6
  transparency rendering; the FE — gate 3 (ux-blueprint MF1/MF2) for the
  roster.

## 8. Threat model (mini-STRIDE)

The contract's assets: **the absence of credential material on the
wire** (as in agent-discovery §8) and **the catalog's
completeness/truthfulness** — the transparency surface must not lie
about the collection surface. Boundaries: (a) harness configs/caches ↔
the agent's reader; (b) agent ↔ board (the authenticated POST); (c)
board ingest ↔ mirror/transparency rendering. The central controls — the
names-only discipline and the closed catalog (P1); every mitigation
below points at a §3 MUST or is marked «operational control».

| Category | Threat | Mitigation | Verification |
|---|---|---|---|
| **I**nformation Disclosure | credential material from a config/cache in the payload | marker fields — presence only → `auth` (§3.3.6); `mcp-cache.json` values never decoded (§3.4); the 8 KiB read cap narrows the read surface (§3.3.5) | `no_credential_material`, `mcp_names_only` |
| **I**nformation Disclosure | a new leg reads beyond the table-named fields (catalog drift) | the closed catalog P1 + the JSON-pointer-level layout table; scan heuristics forbidden (§3.1, §3.3.2); the transparency rendering shows EVERYTHING collected — a code-vs-catalog divergence is visible to the owner (§3.6) | `models_field_shape` + table review (operational control) |
| **I**nformation Disclosure | a credential-shaped string in a free field (`note`) | the names-only validator: the WHOLE row dropped before marshal, a loud log without the value (§3.3.6); the board detector — the second line (§4) | `no_credential_material` |
| **I**nformation Disclosure | a credential in the URL | `base_url` normalization (§3.3.6): query/fragment/userinfo always stripped; unparsable — omit | `base_url_normalized` |
| **I**nformation Disclosure | the harness-configured probe as a channel to a foreign/credentialed endpoint | LOOPBACK only; `auth: configured` → never dialed; ≤8 targets; zero-redirect; one GET, quiet zero (§3.3.4; H3) | the probe-rule review (operational control) |
| **S**poofing | a foreign executor reports | the route's executor-token + identity-match (inherited; agent-discovery §3.1) | route integration tests (operational control) |
| **E**levation of Privilege | a discovery fact grants itself authority | advisory, never authority: the field creates no rows, extends no dictionaries (agent-discovery §3.1, §3.11) | board conformance (operational control) |
| **D**enial of Service | a bloated report (frontmatter ≤64 files × legs) chokes the board | shrink-to-fit (§3.3.5); the family's honest 422 (§4); the hourly cadence without its own timer | `row_caps`, `mcp_names_cap30` |
| **R**epudiation | «who dropped the row / who sent a credential?» | drops audited, incidents named, the local log loud (§3.3.6, §4) | operational control (the board's audit trail) |
| **T**ampering | the transparency rendering lies about the surface (catalog drift between the board's and the agent's contract versions) | the agent↔contract version handshake (§3.6); the field → FC map complete (§3.2); a field without an FC id = a defect | operational control (handshake tests) |

Conscious residual risks: a harness process reads its OWN configs — the
harness's threat model, not the fleet's (gate 2 §6); full board-host
compromise — outside the agent wire; MCP server names on the board —
advisory metadata of the same sensitivity as provider names.

## 9. Migration and implementation status

The legacy leg: v6 (AGW-25) rides the wire — its standalone table is
superseded, but the field is compatible (§7). The legs' status —
honestly:

| Leg | Status | Where it lives |
|---|---|---|
| Agent v6 (standalone `models`) | **rode the wire** (AGW-25, merged 2026-10-28) — SUPERSEDED by this contract's population rules; zero rows on the real fleet (verified live 2026-10-28 on core-51: the four v6 config files are absent; the fleet's real harnesses — zcode/copilot — carry their catalogs in agent-definition frontmatter) | vesmaro/vesma-agent, main (merge b98960e); `docs/PROTOCOL.md` §3 |
| Agent v7 (per-harness re-key + FC-7) | **in flight** — the `feat/host-intake-contract` branch, AGW-26; the contract draft — `docs/design/host-intake-contract-draft.md` (this spec's source) | vesmaro/vesma-agent |
| Board mirror of the new fields (ingest of per-harness `models`, `mcp_servers`; the §3.6 transparency rendering) | **not merged** — a separate vesma-eyes wave (pending; contract §9) | vesma-eyes |
| FC-8 / FC-9 | **DEFERRED (v2)** — the owner's decision at the draft gate; activation = a minor of this contract with a gate | — |

`sessions[]` — outside the agent's collection surface (verified
2026-10-28): the field exists in the board's `ExecutorDiscoveryBody`
(the additive ME-062 leg: task-linked session facts, the
task-session-fact store, drops audited as `sessions.rejected`), but it
is fed by the board's eyes-side scanner (the kora-scan ingest
`POST /api/executors/{id}/kora-scan`; cluster sessions — the synthetic
executor id `hermes`), not by the agent: the agent's Go code
(`internal/discovery`, `internal/board`) constructs no session facts —
the word "sessions" appears only as a directory-store name in the FC-2
fingerprint markers (store name + count, the v3 discipline). For the
agent the field is absent; honest absence (P4).

Input order: (1) the spec (this document) — done; (2) the agent wave v7
(AGW-26): the re-key + FC-7, fixtures on the GROUNDED shapes, gates +
cascade, release v0.11.0, fleet update — the standing wave discipline
(contract §10); (3) the board mirror wave — ingest + the transparency
rendering; (4) stable ratification — both sides' conformance green.
Intermediate states are conformant by additivity (§7).

## 10. References

- Owner directive 2026-10-28 — two clauses (the per-harness re-key; the
  explicit collection-surface contract): this contract's authority;
  duplicated in the header and the [CHANGELOG](CHANGELOG.md).
- The agent-side contract draft —
  `docs/design/host-intake-contract-draft.md` (vesmaro/vesma-agent, the
  `feat/host-intake-contract` branch): the source of the catalog, the
  P1–P6 principles, the per-harness table, the red lines; its gates
  (OQ-1…OQ-5) are owner-approved.
- Gate 2 — `docs/design/models-fleet/security-verdict.md`
  (vesmaro/vesma-eyes, the `feat/models-fleet-blueprint` branch,
  832cd7a): the carried red lines (names-only, URL normalization,
  auth-from-presence, the anonymous probe H3, the board-side detector).
- [specs/agent-discovery/v0/spec.md](../../agent-discovery/v0/spec.md)
  (0.1.0-draft.2) — the `models` field's wire discipline (the row form,
  snapshot/no-wipe, board ingest duties, the §4 route codes); this
  contract does not re-litigate it, it populates it.
- [ADR-0001](../../../adrs/0001-repo-structure-and-governance.md) — the
  layer's structure and governance; the contract's form.
- [ADR-0002](../../../adrs/0002-agent-discovery-contract.md) — the
  agent-discovery codification (the predecessor).
- [ADR-0003](../../../adrs/0003-host-intake-catalog.md) — the explicit
  collection-catalog decision (this spec's authority trail).
- The TL spec-phase brief 2026-10-28 — the spec-phase wave budgets laid
  over the approved gates: ≤64 frontmatter-read files, ≤8
  harness-configured probe targets, the `discovery_models` knob for
  FC-7, `count` = the full total, the pi provider `pi` row with the
  `models` field omitted (omitempty), the per-row note as the OQ-5 wire
  form.
- The [glossary](../../../GLOSSARY.md), the
  [ecosystem map](../../../ECOSYSTEM.md), the
  [roadmap](../../../docs/roadmap.md).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword
  interpretation.
