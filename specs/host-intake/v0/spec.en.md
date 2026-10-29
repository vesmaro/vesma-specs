---
contract: host-intake
version: 0.1.0-draft.6
status: draft
decisions: [ADR-0001, ADR-0002, "owner directive 2026-10-28 (two clauses: per-harness models re-key + the explicit collection-surface contract)", "the agent-side contract draft — docs/design/host-intake-contract-draft.md (vesmaro/vesma-agent, the feat/host-intake-contract branch); the draft's gates are owner-approved (FC-6+FC-7 this wave; the loopback probe approved; dual-form emission approved; FC-8/9 initially DEFERRED to v2)", "gates carried: fleet security-verdict (vesma-eyes, feat/models-fleet-blueprint, 832cd7a) — the red lines", "the AGW-25/AGW-26 lineage (discovery v6 → v7 re-key)", "the discovery v8 amendment (AGW-27, 2026-10-29; the owner's «делай» directive 2026-10-29): FC-8/FC-9 un-deferred → normative (§3.4a/§3.4b), the discovery_host_facts knob, the discovery_models_catalogs knob (owner-declared model catalogs)", "the discovery v9 amendment (AGW-28, 2026-10-29; the owner's «делай» directive 2026-10-29): the FC-6/FC-7 «metal only» red line LIFTED for config reads through distrobox container probes (§3.4c) — running containers join the surfaces; per-surface row identity (provider, base_url, model, harness, exec_env); FC-7 from containers (entry-level detector); the pi marker inside containers — existence-only `test -f`; quiet degradation without the distrobox CLI; knobs unchanged (discovery_models + discovery_distrobox)", "the discovery v10 amendment (AGW-29, 2026-10-29; the owner's architectural directive of 2026-10-29 «Не надо заходить в контейнер, чтобы найти файлы его — все есть на хосте (как подключаемый том)!» — do not enter the container to find its files, they are all on the host, like a mounted volume): the §3.4c container-read mechanism REPLACED — direct host-path reads of the homes `<root>/.distrobox/<box>/home` (a glob per discovery root, pure stat; structural gating as metal — fingerprint-discovered homes only; metal-wins dedupe — a home path already covered by a metal root is not re-scanned as a container home, test-pinned); the fence transport of draft.4 (released in vesma v0.5.0) is deprecated and removed from the agent; the v4 enter-based leg stays — binary/version probes only; the knob clarification: the container-home walk + the models/mcp reads ride `discovery_models`, `discovery_distrobox` gates only the v4 CLI leg", "draft.6 — version note: the credential-shape scan's class list is normative in [agent-discovery §3.8](../../agent-discovery/v0/spec.md) (0.1.0-draft.3: the JWT shape and the long mixed run, agent↔board parity; issue vesmaro/vesma-specs#10); host-intake does not restate the class list — §3.3.6 carries the pointer only"]
ratified: |-
  Not ratified (draft). Authority trail: owner directive 2026-10-28 —
  two clauses (per-harness models re-key; the explicit collection
  surface as the trust/transparency surface); the agent-side contract
  draft (docs/design/host-intake-contract-draft.md, vesmaro/vesma-agent,
  feat/host-intake-contract) is the source of the catalog, principles,
  the per-harness table and the disciplines; its gate decisions are
  owner-approved (FC-6+FC-7 this wave, the loopback probe approved,
  dual-form emission approved; FC-8/9 initially deferred to v2); the
  config-read red lines carry over from the ratified security-verdict
  (832cd7a, models-fleet gate 2); the protocol lineage is AGW-25
  (discovery v6, merged) → AGW-26 (v7 re-key) → AGW-27 (discovery v8,
  2026-10-29 — this spec's amendment: FC-8/FC-9 normative, the
  discovery_host_facts and discovery_models_catalogs knobs) → AGW-28
  (discovery v9, 2026-10-29 — this spec's amendment: the «metal only»
  red line lifted for distrobox container probes, §3.4c; the owner's
  «делай» directive of 2026-10-29; the agent-side normative form — the
  «Container-surface addendum — discovery v9 (AGW-28, 2026-10-29)»
  addendum in vesma-agent's docs/PROTOCOL.md, landing in parallel) →
  AGW-29 (discovery v10, 2026-10-29 — this spec's amendment: the
  §3.4c mechanism replaced with direct host-path reads of container
  homes; the owner's architectural directive of 2026-10-29).
  Stable ratification — the first conformant implementation of the
  catalog legs by the agent (v7+) and a green conformance run.
language: en (informative mirror)
---

# host-intake v0 — the explicit host-collection catalog contract

> This is an informative English mirror of the normative Russian
> specification [spec.md](spec.md). In case of divergence, the Russian
> text prevails. The mirror is maintained in the same change as the
> Russian text (single-commit sync policy).
>
> **Status: draft (0.1.0-draft.5).** The contract fixes the COMPLETE
> explicit catalog of what the outbound ЦУП agent (`vesmaro-agent`)
> collects on a host — the fleet's trust and transparency surface
> (clause 2 of the owner directive 2026-10-28) — and normatively defines
> the new/re-keyed legs: FC-6 (models per-harness — the re-key
> superseding the v6 standalone table of AGW-25), FC-7 (mcp_servers),
> since the discovery v8 amendment (AGW-27, 2026-10-29; the
> owner's «делай») — FC-8 (tooling, §3.4a) and FC-9 (compute envelope,
> §3.4b), whose DEFERRED status is lifted, and — since the discovery v9
> amendment (AGW-28, 2026-10-29; the owner's «делай») — FC-6/FC-7
> configs in distrobox container homes (§3.4c): the «metal
> only» red line is lifted for containers; since the discovery v10
> amendment (AGW-29, 2026-10-29; the owner's architectural directive
> «Не надо заходить в контейнер, чтобы найти файлы его — все есть на
> хосте (как подключаемый том)!») the §3.4c mechanism is DIRECT
> host-path reads (`<root>/.distrobox/<box>/home` — host-visible
> paths); the fence transport of draft.4 (released in vesma v0.5.0)
> is deprecated and removed from the agent. Anything not named in the
> catalog of §3.2 is not collected. Form changes after ratification go
> through the SemVer process only (ADR-0001 §2).

The key words MUST / MUST NOT / SHOULD / MAY are interpreted per
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). Prose is English;
identifiers, fields and enum values are EN. Every requirement traces to
the agent-side contract draft («contract §…» =
`docs/design/host-intake-contract-draft.md`, its gates owner-approved on
2026-10-28), the carried security-verdict («gate 2», 832cd7a), the
AGW-25/AGW-26 protocol lineage, or the discovery v8/v9/v10 amendments
(AGW-27, AGW-28 and AGW-29, 2026-10-29 — the TC-pinned deltas;
v8/v9 were owner-approved with «делай» on 2026-10-29, v10 by the
owner's architectural directive of 2026-10-29; the agent-side
normative form — the «discovery v8 (AGW-27, 2026-10-29)» and
«Container-surface addendum — discovery v9 (AGW-28, 2026-10-29)»
addenda in vesma-agent's `docs/PROTOCOL.md` — the latter amended by
the v10 addendum to host-path reads, landing in parallel); the text
marks them. Budgets marked «(brief 2026-10-28)» and
«(brief 2026-10-29)» are spec-phase wave budgets laid over the approved
gates (listed in §10).

## 1. Scope

The contract fixes the **explicit collection catalog** — the complete
list of fact classes (FC) the agent may gather on a host, with the
surface principles (P1–P6), the normative wire forms of the normative
legs (FC-6…FC-9), and the never-collected boundary. The trust
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
- FC-8 — tooling: presence + version of the fixed built-in host-tool
  list, the `discovery_host_facts` knob (§3.4a; normative since
  discovery v8, AGW-27);
- FC-9 — compute envelope: CPU cores, RAM total, disk free, GPU names,
  the `discovery_host_facts` knob (§3.4b; normative since discovery v8,
  AGW-27);
- owner-declared model catalogs — the `discovery_models_catalogs` knob
  as an extension of the FC-6 per-harness table (§3.3.2; discovery v8,
  AGW-27);
- container config surfaces — FC-6/FC-7 config reads in distrobox
  container homes over DIRECT host paths: the homes
  `<root>/.distrobox/<box>/home` are host-visible paths and join the
  surfaces, per-surface row identity, the mechanism = plain bounded
  host file reads (a `<root>/.distrobox/*/home` glob per discovery
  root, pure stat; structural gating as metal; §3.4c; discovery v9
  AGW-28, the mechanism replaced by discovery v10, AGW-29);
- the board's transparency surface: rendering "what agents collect"
  FROM this contract, per agent version; the field → FC map (§3.6);
- the honest implementation status (§9).

**Out of scope (neighbouring domains):**

- pod config surfaces (`exec_env` = `pod:<name>`) — the follow-up
  wave; the discovery v9 (AGW-28) and v10 (AGW-29) amendments lift
  «metal only» ONLY for distrobox container homes (§3.3.6, §3.4c,
  §9);
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
| per-surface row identity | The identity of an FC-6/FC-7 config-fact row — the tuple `(provider, base_url, model, harness, exec_env)` (the discovery v9 amendment, AGW-28): the SAME provider+model configured on metal AND in a container = TWO rows — config facts are per-surface. The v4 «one namespace, one truth» dedupe applies to ENVIRONMENT homes (the FC-2 exec_env merge), not to config-fact rows (§3.3.1, §3.4c). |
| never collected | The catalog's verbatim boundary: file contents (outside the named per-class exceptions), project/workspace names, prompts and session content, environment-variable VALUES, network traffic, credential material in any form (§3.5). |
| transparency surface | The board's rendering of "what agents collect" FROM this contract, per agent version: one card per FC id (what, why, caps, privacy line); built via the contract↔agent version handshake (§3.6; contract §7). |
| harness bucket | The FC-6 provider attribution when NO documented string form parses: provider = the harness slug; the reason is a local-log fact, never the wire; an advisory name board-side (§3.3.3). Provider guessing is forbidden (contract §3.2; draft gate OQ-3: never guess). |
| dual-form emission | The OQ-3-approved emission form of FC-6: `models[]` carries the RAW frontmatter/config strings verbatim; the parsed provider rides the row's `provider` field — and only when the documented form parses (§3.3.3). |
| DEFERRED (v2) | A catalog-class status: the class is described (what, source, caps), implementation deferred by the owner's decision; the agent does NOT collect it until activation (§3.2, §9). Initially carried by FC-8/FC-9; the deferral was lifted by the discovery v8 amendment (AGW-27, 2026-10-29, the owner's «делай») — the status is unused in the catalog now and stays in the status vocabulary for possible future deferrals. |
| leg knob | A leg's configuration switch in the agent config with enum values (the agent-discovery §3.9 precedent): `auto` — the leg runs; `off` — the leg's fields are absent from the wire entirely; an unknown value — refuse to start (never a silent fallback). This contract's legs carry two knobs: `discovery_models` (FC-6/FC-7, §3.3/§3.4) and `discovery_host_facts` (FC-8/FC-9, §3.4a/§3.4b); the FC-6 extension — the `discovery_models_catalogs` list (§3.3.2). Container reads of FC-6/FC-7 (§3.4c; the container-home walk + the models/mcp reads in them) ride `discovery_models` ONLY, with NO new knobs; `discovery_distrobox` (the v4 knob of the FC-4 container leg) gates ONLY the v4 CLI leg (binary/version probes) and is NOT required for the §3.4c host-path reads (the discovery v10 clarification, AGW-29). |

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
| FC-6 | `models` per-harness | Per DISCOVERED harness: configured providers (name, base_url normalized, auth enum), available models (what the config/catalog names + anonymous local-server availability), default model | the §3.3.2 per-harness layout table; since v9 (AGW-28) — the same files in distrobox container homes (§3.4c; direct host-path reads since v10, AGW-29) | names/enums/normalized URLs | 64 rows (across surfaces), 50/row, 16 KiB (across surfaces), 8 KiB/file | **re-key (v7, AGW-26)** — supersedes the v6 standalone table; container surfaces since v9 (AGW-28) |
| FC-7 | `mcp_servers` per harness | MCP/extension server NAMES + transport kind | documented caches/configs (pi `mcp-cache.json`; zcode/copilot mcp sections where documented); since v9 (AGW-28) — the same caches in distrobox container homes (entry-level detector, §3.4c) | names/kinds only — never argv, env, URLs | ≤30 names per element (harness × exec_env), 8 KiB/element | **approved (v7)** — new; container entries since v9 (AGW-28) |
| FC-8 | tooling | Presence + version of a FIXED built-in host-tool list (git, podman, docker, python3, node, go, …) | LookPath + ONE version call ≤2 s (brief 2026-10-29) | names/versions; the version — first line ≤200 runes through the names-only validator, drop-on-shape | ≤40 tools sorted + honest `count`; 8 KiB shrink-to-fit | **normative (v8, AGW-27)** — §3.4a |
| FC-9 | compute envelope | CPU cores, RAM total, disk free on the state volume, GPU presence (names only) | /proc + statvfs + ONE `nvidia-smi -L` call (brief 2026-10-29) | numbers only; GPU names — strings ≤8, validator-gated; never serials/utilization | fields omitempty INDEPENDENTLY (P4); one-shot per pass | **normative (v8, AGW-27)** — §3.4b |

**MUST**: the status column changes only through a contract amendment
(P5); activating a DEFERRED class = such an amendment with an owner
gate (P1: adding a collected class is always gated). The discovery v8
amendment (AGW-27, 2026-10-29; the owner's «делай») lifted DEFERRED
from FC-8/FC-9 — both classes are normative (§3.4a, §3.4b) and
governed by the `discovery_host_facts: auto|off` knob (§3.4a). The
discovery v9 amendment (AGW-28, 2026-10-29; the same «делай»
directive) extended the FC-6/FC-7 SOURCES with distrobox container
homes (§3.4c) — the classes and fields are unchanged, the FC-6
caps became surface-spanning totals. The discovery v10 amendment
(AGW-29, 2026-10-29) replaced the CONTAINER-READ MECHANISM (the
draft.4 fence transport → direct host-path reads, §3.4c) — the
classes, fields, caps and wire form are unchanged.

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
| `tooling` (since v8, AGW-27) | FC-8 |
| `compute` (since v8, AGW-27) | FC-9 |
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
- **MUST** (discovery v9, AGW-28): a config-fact row's identity — the
  per-surface tuple `(provider, base_url, model, harness, exec_env)`:
  the SAME provider+model configured on metal AND inside a container =
  TWO rows (one per surface) — config facts are per-surface.
  **MUST NOT**: cross-surface deduplication of rows; the v4 «one
  namespace, one truth» principle (the dedupe identity from agent-side
  `os.Stat`) applies to ENVIRONMENT homes (FC-2, the exec_env merge),
  NOT to config-fact rows.

#### 3.3.2 The per-harness layout table (built-in, typed decodes, the v3 discipline)

| harness | source | fields named by the table | credential marker (presence only) | grounded |
|---|---|---|---|---|
| zcode | `~/.zcode/agents/*.md` frontmatter (frontmatter-first read; ≤64 files, 8 KiB/file — brief 2026-10-28); + owner-declared model catalogs via the `discovery_models_catalogs` knob (v8, AGW-27 — the block below) | `model:` (scalar or list — try-in-order), `tier:`, agent `name:` (provider from the documented string forms: the `(provider)` suffix, the `provider/model` prefix; display-name and qualified id are both legal) | — (tier arrays carry provider slugs) | 2026-10-28: the GCW installer renders the fleet `models.yaml` into these files; live ids documented (`ollama-cloud/glm-5.3-flash`, `z/glm-5.3`) (contract §3.2) |
| copilot | `~/.copilot/agents/*.agent.md` frontmatter (same budgets) | the same `model:`/`tier:` fields; the `" (copilot)"` suffix convention | — | 2026-10-28: `model: GLM 5.3 Flash (ollama-cloud)`, `tier: 1` verified live; GitHub-side model catalogs are server-only — the LOCAL fact is what the definitions name (the server-only honesty lives in this description/the catalog, not on the wire row) (contract §3.2) |
| codex | `~/.codex/config.toml` | top-level `model`, `model_provider`; `model_providers.<name>.{name, base_url, env_key}` | `env_key` non-empty → configured | v6, carried (contract §3.2; AGW-25) |
| continue | `~/.continue/config.json` | `models[].{provider, model, apiBase, apiKey}` | the `apiKey` field present → configured | v6, carried (AGW-25) |
| claude-code | `~/.claude/settings.json` | `model`; from `env` — only KEY NAMES with the `ANTHROPIC_` prefix | any `ANTHROPIC_*` name → configured; none → unknown | v6, carried (contract §3.2; AGW-25) |
| aider | `~/.aider.conf.yml` | `model`, `openai-api-base`, `openai-api-key` | `openai-api-key` present → configured; absent → unknown | v6, carried (AGW-25) |
| pi | `<home>/.pi/agent/` | no documented model catalog today → honest absence (model rows: none); `auth.json` EXISTENCE → the pi auth fact | `auth.json` exists → configured (the value is NEVER read); no file → unknown; in a container home (v9, AGW-28; the host-path form v10, AGW-29) the marker = an existence-only stat of the same host path (`test -f`) — the read never touches the file's bytes (§3.4c) | 2026-10-28: `auth.json` present on core-51's pi (contract §3.2); emission: one provider `pi` row, the `models` field omitted (omitempty; an empty list would be a zero-and-ran claim — the key is not emitted) (brief 2026-10-28) |

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

**Owner-declared model catalogs — the `discovery_models_catalogs` knob
(FC-6; discovery v8, AGW-27, 2026-10-29):**

- **MUST**: the `discovery_models_catalogs` knob — a YAML list of
  `{path, harness}` entries: EXPLICITLY owner-declared model-catalog
  files (P1: the agent NEVER discovers catalog paths by itself — only
  owner entries; the GCW `models.yaml` precedent — the `tiers` dict of
  `primary`/`fallback` strings of the `Name (vendor)` form; grounding:
  the GCW repository's models.yaml).
- **MUST**: the catalog file is read under a DEDICATED 64 KiB read
  cap (the item below); a TYPED decode
  (the `tiers` structure — a dict tier → `{primary, fallback[]}`);
  ALL model strings are collected — primaries AND fallbacks (P5: the
  full catalog, not the primary only).
- **MUST**: the catalog read cap — DEDICATED 64 KiB per
  `discovery_models_catalogs` ENTRY (synced with the agent
  implementation v0.12.1, `catalogReadLimit = 64 KiB`: the real GCW
  `models.yaml` — 8949 bytes — did not fit the 8 KiB cap); the
  entry's path is EXPLICITLY owner-declared — a higher bounded cap is
  honest for an owner-declared path, unlike walks over foreign
  harness configs; a file over 64 KiB = the entry's honest absence
  (P4; skip + an info log); the walked harness config files (the
  table above) keep the 8 KiB cap UNCHANGED.
- **MUST**: provider attribution — by the documented string forms
  (§3.3.3, suffix-priority: the `(provider)` suffix form is tried
  first, then the `provider/model` prefix); no form parsed → the
  harness bucket of the entry's harness (§3.3.3, never guess).
- **MUST**: a catalog row carries `source: config`, `auth: unknown` and
  the note «model catalog (owner-declared)» — the owner declares a
  configuration fact; the table names no credential-marker field in a
  catalog file (P3: catalog values are model names, not credential
  material; auth unknown, not anonymous — the §3.3.2 pi precedent).
- **MUST**: the row's `harness` = the spelling from the OWNER's ENTRY
  (the entry's `harness` field, verbatim); the board dictionary decides
  admission (unknown → drop + audit, agent-discovery §3.11). Difference
  from the §3.3.1 structural attribution: frontmatter/config rows are
  possible only for a harness DISCOVERED by the inventory; a catalog
  row is an owner-declared fact — its admission is decided by the board
  dictionary, not by the agent's discovery (AGW-27).
- **MUST**: an invalid entry (missing `path`/`harness`, unreadable or
  non-regular file, over 64 KiB, unparsable YAML, decode mismatching the
  typed form) = skip the entry + an info log — never an error, never a
  guess (P4; quiet zero).
- **MUST**: catalog rows ride the common FC-6 `models` field and are
  governed by the `discovery_models: auto|off` knob (§3.3/§3.4):
  `off` → the `models` field is absent entirely, no catalog rows. The
  catalog PATHs NEVER ride the wire — only the catalog's model strings
  (§3.5).

#### 3.3.3 The documented provider string forms (dual-form emission, never guess)

The documented string forms of frontmatter/config model rows (contract
§3.2; draft gate OQ-3 approved):

- **MUST**: form 1 — the `(provider)` suffix: `Model Name
  (provider-slug)` → provider = the slug; the raw string rides
  `models[]` verbatim.
- **MUST**: form 2 — the `provider/model` prefix: a qualified id
  (`ollama-cloud/glm-5.3-flash`) → provider = the prefix, model id = the
  rest.
- **MUST**: form 3 — the literal vendor form `(copilot)`: the suffix
  is a space followed by `(copilot)` → provider = `copilot`; the GitHub-side catalog is
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
- **MUST** (discovery v9, AGW-28): the `installations[]` and `models`
  object caps are SPANNING ACROSS SURFACES: 64 rows and 16 KiB —
  TOGETHER on metal and in all containers (the per-surface rows of
  §3.3.1 get no separate caps); `models[]` ≤ 50 stays per-row.
- **MUST**: the zcode/copilot frontmatter-first read: ≤64 agent
  definition files per pass (brief 2026-10-28), each under the 8 KiB
  read cap; a container home (§3.4c): ≤64 files per container
  home — the same budget per EACH surface separately (a walk budget,
  not an object cap).
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
  length caps + the credential-shape scan. The scan's class list is
  normative in [agent-discovery
  §3.8](../../agent-discovery/v0/spec.md) — it is NOT restated here
  (the single source of truth; agent↔board parity is mandatory);
  since 0.1.0-draft.3 it includes the JWT shape and long mixed runs
  (issue vesmaro/vesma-specs#10).
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
- **MUST**: `exec_env` — `"metal"` and, since the discovery v9
  amendment (AGW-28, 2026-10-29; the owner's «делай»),
  `"distrobox:<name>"` for config reads in distrobox container homes
  §3.4c: the FC-6/FC-7 «metal only» red line is LIFTED for distrobox
  containers — the mechanism = DIRECT host-path reads of the homes
  `<root>/.distrobox/<box>/home` (the draft.4 fence transport
  replaced by the discovery v10 amendment, AGW-29); pod config
  surfaces (`pod:<name>`) stay outside the surface (contract §3.4;
  the discovery v9/v10 amendments).

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
  only; `exec_env` — `"metal"` and, since the discovery v9 amendment
  (AGW-28), `"distrobox:<name>"`: container entries ride the same
  form — the detector is ENTRY-LEVEL (one element per the
  harness × exec_env pair; §3.4c).
- **MUST**: `servers[]` — sorted names ≤30 per element (contract §4);
  **MUST**: `count` — the FULL total of names found, even when
  `servers[]` is truncated at 30 (an honest counter; brief 2026-10-28).
- **MUST**: the sources — documented caches/configs ONLY, typed decodes:
  pi `~/.pi/agent/mcp-cache.json` — the `servers` field is a DICT: the
  server names are ONLY the dict KEYS of that map; the cache VALUES are
  never decoded (the landed AGW-26 shape; the contract draft's list
  wording `{version, servers[]}` was wrong and is being fixed on the
  agent-repo side); zcode/copilot mcp sections — where documented
  (contract §4); since v9 (AGW-28) — the SAME caches in
  distrobox container homes (read over direct host paths, §3.4c): a
  container pi's `mcp-cache.json` → an element
  with `exec_env="distrobox:<name>"`, the detector ENTRY-LEVEL
  (a container's and the metal cache of one harness = two elements,
  one per surface; caps unchanged, §3.4c).
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

### 3.4a FC-8 — tooling (normative; discovery v8, AGW-27)

Status: DEFERRED lifted by the discovery v8 amendment (AGW-27,
2026-10-29; the owner's «делай»). The spec pins the COLLECTION
DISCIPLINE; the built-in tool list itself is agent-side ratification
(versioned in the agent, ~25–30 well-known host tools: git, podman,
docker, python3, node, go, …).

- **MUST**: the `discovery_host_facts: auto|off` knob (default `auto`;
  an unknown value — refuse the agent start, never a silent fallback)
  governs FC-8 and FC-9 JOINTLY: `off` → the additive top-level
  `tooling` and `compute` fields are absent from the wire ENTIRELY;
  a run (`auto`) → the fields are present, individual facts may be
  empty or omitted (honest absence, P4; the knob precedent,
  agent-discovery §3.9).
- **MUST**: per tool from the built-in table — LookPath + ONE version
  invocation, timeout ≤2 s (brief 2026-10-29); not on PATH,
  failure/timeout/unparsable output → quiet zero per tool (P4), never
  an error, never a retry.
- **MUST**: the version string — the FIRST line of the output, ≤200
  runes, through the names-only validator (length caps + the
  credential-shape scan, §3.3.6 — drop, never mangle); a
  credential-shaped version string → drop the `version` field (the
  entry stays name-only), the value is never echoed (drop-on-shape; P3).
- **MUST**: the wire — an additive top-level member:

```json
{"tooling": {"tools": [{"name": "git", "version": "2.47.1"},
                       {"name": "python3"}],
             "count": 2}}
```

- **MUST**: the member = `{tools[], count}`; an entry = `{name,
  version?}` — `version` omitempty (no version obtained → a name-only
  entry, honest absence, never a guess); a tool NOT on PATH → no entry
  at all (the class emits PRESENCE facts: an absent tool = an absent
  entry — quiet zero).
- **MUST**: `tools[]` sorted by name, ≤40 (contract §2 FC-8); **MUST**:
  `count` — the FULL total of tools found, even when `tools[]` is
  truncated at 40 (an honest counter; the count semantics of §3.4).
- **MUST**: the field cap — 8 KiB marshaled, shrink-to-fit before send
  (§3.3.5); on truncation the `count` stays full (§3.4).
- Container-runtime tools (podman/docker) are collected as
  PRESENCE/VERSION facts — this class touches no container config
  surfaces: container reads are the FC-6/FC-7 domain (§3.4c;
  §3.3.6, §9); FC-8/FC-9 have no `exec_env` dimension.

### 3.4b FC-9 — compute envelope (normative; discovery v8, AGW-27)

Status: DEFERRED lifted by the same amendment (AGW-27). The class is a
hardware-envelope fact set; the privacy line: the hardware envelope
only — no hostnames, serials or machine identifiers beyond the class
facts (§3.5).

- **MUST**: the wire — an additive top-level member; EVERY field is
  omitempty INDEPENDENTLY by honest absence (P4: no reliable fact → no
  field, never a zero placeholder):

```json
{"compute": {"cpu_cores": 16, "mem_total_bytes": 33554432000,
             "disk_free_bytes": 107374182400,
             "gpus": ["NVIDIA GeForce RTX 4090"]}}
```

- **MUST**: the member = `{cpu_cores?, mem_total_bytes?,
  disk_free_bytes?, gpus?}` — NUMBERS ONLY (integers; memory/disk in
  bytes; `cpu_cores` — logical cores). `disk_free_bytes` — free space
  on the state volume (contract §2 FC-9).
- **MUST**: GPU — ONE `nvidia-smi -L` call per pass (brief 2026-10-29);
  NAME strings ONLY, ≤8 entries, through the names-only validator
  (§3.3.6); **MUST NOT**: serials, utilization, telemetry — ever; a
  failed call, unparsable output, or names beyond 8 → `gpus` is omitted
  or honestly truncated (P4; honest truncation — drop, never mangle).
- **MUST**: the cap — shrink-to-fit 8 KiB marshaled (the family
  discipline of §3.3.5); an over-cap field is an honest 422 board-side
  (§4).
- **MUST**: knobs and honest absence — as in §3.4a (the single
  `discovery_host_facts: auto|off`; quiet zero per fact; one-shot per
  pass, no timer of its own).

### 3.4c Container config surfaces — direct host-path reads (FC-6/FC-7; discovery v9, AGW-28 → v10, AGW-29)

Status: the discovery v9 amendment (AGW-28, 2026-10-29; the owner's
«делай» directive of 2026-10-29) lifted the FC-6/FC-7 «metal only» red
line (§3.3.6) — containers join the collection surfaces; its mechanism
(bounded fence transport through `distrobox enter`) was REPLACED by
the discovery v10 amendment (AGW-29, 2026-10-29) under the owner's
architectural directive of 2026-10-29: «Не надо заходить в контейнер,
чтобы найти файлы его — все есть на хосте (как подключаемый том)!»
(do not enter the container to find its files — they are all on the
host, like a mounted volume). Distrobox container homes are
HOST-VISIBLE paths (`<root>/.distrobox/<box>/home/...`), and FC-6/
FC-7 are read in them as ordinary bounded host files: no transport,
no base64, no fenced blocks, no generated scripts, no `distrobox
enter`. The fence-transport machinery of draft.4 (released in vesma
v0.5.0) is DEPRECATED and REMOVED from the agent (AGW-29); the v4
enter-based leg (FC-4) STAYS — binary/version probes only. The
agent-side normative form — the addendum in vesma-agent's
`docs/PROTOCOL.md` amending «Container-surface addendum — discovery
v9 (AGW-28, 2026-10-29)» to host-path reads (landing in parallel).
Pod surfaces (`pod:<name>`) stay outside the surface (§1).

- **MUST**: container-home discovery — a `<root>/.distrobox/*/home`
  glob (pure stat, no CLI) on EVERY discovery root; structural gating
  AS ON METAL: a container home becomes a collection surface only
  when the built-in fingerprint table (FC-2) ACTUALLY discovers a
  harness home in it (the same markers, the same rules;
  fingerprint-discovered homes only).
- **MUST**: the fingerprint walk applies inside a container home
  VERBATIM (the same markers/rules) — the structural invariant «the
  same method as on metal»; the FC-6/FC-7 layout reads in a container
  home are PLAIN bounded host file reads: the same caps (≤64 files
  per container home, the hard 8 KiB read cap per file — §3.3.5), the
  same typed decodes (§3.3.2/§3.3.3), the names-only validator —
  unchanged. **MUST NOT**: no transport of any kind — no base64, no
  fenced blocks, no generated scripts, no `distrobox enter` for
  config reads (the draft.4 fence transport is removed from the
  agent; AGW-29).
- **MUST** (metal-wins dedupe): a home's absolute path already covered
  by a metal discovery root is NOT re-scanned as a container home —
  the agent's own box home is metal truth; the rule is test-pinned
  (the agent's tests).
- **MUST**: container state does not gate the reads: the home is read
  as a host path regardless of running/stopped — no enter is
  executed, a side effect is impossible by construction; the v4
  honest-verdict machine (including `not-running`) and its CLI budget
  «30 s leg / 20 s probe» remain in FC-4 — the enter-based leg of
  binary/version probes.
- **MUST**: the pi auth marker in a container home — an existence-only
  stat of the same host path (§3.3.2): the read never touches the
  bytes of `auth.json` — a boolean fact, not content.
- **MUST**: quiet degradation: a `.distrobox` subtree absent → zero
  container homes, quiet zero (the COMMON case of hosts without
  boxes; not an error, not a retry); an unreadable/non-regular
  container home = that home's honest absence (P4).
- **MUST**: knobs — PRECISELY: the container-home walk itself and the
  models/mcp reads in it ride `discovery_models: auto|off`
  (FC-6/FC-7); `discovery_distrobox` (the v4 knob) gates ONLY the v4
  CLI leg (FC-4 distrobox_containers) and is NOT required for the
  §3.4c host-path reads; no new knobs (P5; the agent-discovery §3.9
  precedent).
- **MUST NOT**: pod config surfaces are not read (honest absence);
  beyond the files the §3.3.2 table names, the read in a container
  home touches NOTHING (the §3.5 boundary applies to a container home
  as to ordinary host files, verbatim).
- **MUST**: rows from container homes carry
  `exec_env="distrobox:<name>"` (name = the `.distrobox/<name>` path
  segment); row identity and caps — per §3.3.1/§3.3.5 (per-surface
  rows; caps span surfaces); FC-7 — the entry-level detector (§3.4).

### 3.5 Never collected (the verbatim boundary)

**Never collected** (contract §2, verbatim): file contents (outside the
named per-class exceptions), project/workspace names, prompts and
session content, environment-variable VALUES, network traffic,
credential material in any form. The MANAGED allowlist and the shim wave
are separate surfaces this contract does not touch. Since the discovery
v8 amendment (AGW-27) the boundary gains explicit lines for the FC-8/
FC-9 hardware classes: **never collected** are hardware serials,
utilization telemetry and load telemetry of any kind; the PATHs of
owner-declared model catalogs never ride the wire — only the catalog
row facts (§3.3.2, §3.4b). Since the discovery v9 amendment (AGW-28)
the boundary gains a container line, reformulated by the discovery
v10 amendment (AGW-29) for the host-path mechanism: container homes
are host-visible paths (`<root>/.distrobox/<box>/home`), and the
bounded-read discipline applies to them AS TO ORDINARY HOST FILES
(§3.4c) — only the NAMED files of the §3.3.2 table are read under the
8 KiB read cap, ≤64 files per container home; NOTHING outside the
table; no transport, no `distrobox enter` (the draft.4 fence
transport is removed from the agent).

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

The contract introduces no new codes: the catalog legs (FC-6, FC-7 and
since v8 — FC-8, FC-9) ride the EXISTING
`POST /api/executors/{executor_id}/discovery` route, and
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
| `422` | `models` over 16 KiB marshaled (across surfaces, §3.4c); `installations[]` > 64 (across surfaces); `models[]` > 50; an `mcp_servers` element over 8 KiB; `servers[]` > 30; `tooling`/`compute` over 8 KiB; `tools[]` > 40; `gpus` > 8; an unknown form enum value — honest rejection, never a silent trim (the agent's shrink-to-fit makes an over-cap send an agent defect) |
| `404` | the FC-6/FC-7/FC-8/FC-9 leg stays silent below info on a board without the route — additivity creates no schedule and no retries (§3.1 P5) |

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
| `examples/tooling-field.json` | the additive top-level `tooling` (FC-8, §3.4a): `{tools[], count}` — `{name, version?}` entries, `version` omitempty for a tool with no version obtained, `count` = the full total, sorted |
| `examples/compute-envelope.json` | the additive top-level `compute` (FC-9, §3.4b): numbers only, fields independently omitempty, `gpus` — names only (never serials/utilization) |
| `examples/catalog-row-owner-declared.json` | an FC-6 row from an owner-declared catalog (the `discovery_models_catalogs` knob, §3.3.2): `source: config`, `auth: unknown`, the note «model catalog (owner-declared)», the catalog's primary+fallback strings, the provider from the documented suffix form |
| `examples/container-installation-row.json` | a container-sourced FC-6 row (§3.4c, discovery v9 AGW-28 → v10 AGW-29): the same provider+model as the metal zcode row but `exec_env: "distrobox:<name>"` — the per-surface identity of §3.3.1 = a DISTINCT row; the read — a direct bounded host-path read of a named file of the container home, no transport artifacts on the wire (§3.5) |
| `examples/mcp-servers-container-entry.json` | a container `mcp_servers` element (§3.4, §3.4c): the entry-level detector — metal pi and a distrobox pi = TWO elements (one per the harness × exec_env pair); names only, `count` = the full total per element |
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
| `mcp_servers_field_shape` | elements `{harness, exec_env, servers[], count}`; `count` — the full total; `exec_env` ∈ `"metal"` \| `"distrobox:<name>"` (§3.4, §3.4c) |
| `mcp_names_cap30` | `servers[]` sorted ≤ 30 per harness (§3.4) |
| `mcp_names_only` | no argv/env/URL-shaped strings in `servers[]`/`transports` — names and kinds only (§3.4) |
| `knob_values` | a `discovery_models` knob declaration — only `auto` \| `off`; governs FC-6 and FC-7 jointly (§3.4) |
| `tooling_field_shape` | top-level `tooling` = `{tools[], count}`; `{name, version?}` entries sorted ≤ 40; `count` — the full total; with the knob `off` the field is absent entirely (§3.4a) |
| `tooling_version_discipline` | a present `version` — ≤200 runes, one line, clean per the names-only validator; a credential-shaped version → the entry has no `version` (drop-on-shape) (§3.4a) |
| `compute_field_shape` | top-level `compute` = `{cpu_cores?, mem_total_bytes?, disk_free_bytes?, gpus?}`; fields — numbers only, omitempty INDEPENDENTLY; with the knob `off` the field is absent entirely (§3.4b) |
| `compute_gpu_names_only` | `gpus` — strings ≤ 8, clean per the validator; no serial-/utilization-shaped strings (§3.4b) |
| `catalog_rows_shape` | owner-declared catalog rows: `source=config`, `auth=unknown`, the note «model catalog (owner-declared)»; `harness` = the owner entry's spelling; the catalog PATH absent from the wire (§3.3.2) |
| `host_facts_knob_values` | a `discovery_host_facts` knob declaration — only `auto` \| `off`; governs FC-8 and FC-9 jointly (§3.4a) |
| `container_rows_shape` | container-sourced FC-6 rows carry `exec_env="distrobox:<name>"`; the same provider+model on metal and in a container = TWO rows (per-surface identity §3.3.1); `installations[]` ≤ 64 and the `models` object ≤ 16 KiB — across surfaces (§3.3.5, §3.4c) |
| `container_mcp_shape` | container `mcp_servers` elements carry `exec_env="distrobox:<name>"`; one element per the harness × exec_env pair (entry-level detector); element caps unchanged — ≤30 names, 8 KiB (§3.4, §3.4c) |

Cases: positive — the §5 wire examples (`examples/…`;
`expect: pass`, `severity: must`; the explanatory
`credential-redaction.json` — outside the cases); negative — the
`conformance/fixtures/invalid/` fixtures (`expect: fail`).

## 7. Compatibility

- **SemVer**: `0.1.0-draft.5`; stable ratification — the first conformant
  agent implementation (v7) and a green conformance run. A breaking
  change = MAJOR + a `max(90 days, 2 minor releases)` window with dual
  support; below 1.0 the window is 14 days (ADR-0001 §2).
- **Additivity**: FC-7 (`mcp_servers`) — a new additive top-level field:
  a board ignoring it stays conformant (the unknown-field rule); an
  older agent without the field stays conformant. FC-8 (`tooling`) and
  FC-9 (`compute`) since v8 (AGW-27) — new additive top-level fields
  with the same discipline: a board without their support stays
  conformant, an older agent stays conformant (§3.4a, §3.4b). The FC-6
  extension — owner-declared catalog rows — extends the POPULATION of
  the existing `models` field additively (the row form unchanged;
  §3.3.2). The FC-6 re-key
  changes the POPULATION rules of the existing `models` field
  (per-harness attribution, frontmatter rows, `base_url` omitempty for
  endpoint-less sources) with the row form UNCHANGED: an old board reads
  the new rows as ordinary installations — additively (§3.1 P5;
  agent-discovery §7). Container rows (v9, AGW-28) do NOT change the
  row form: `exec_env="distrobox:<name>"` is a legal value of the
  FROZEN `exec_env` vocabulary (agent-discovery §2, the discovery v4
  precedent), so a board without container support reads them as
  ordinary rows of the same form; the «metal only» lift extends the
  POPULATION, not the form — additive (§3.4c). The discovery v10
  amendment (AGW-29, 2026-10-29; draft.5) changes ONLY the agent-side
  read mechanism of the container surfaces (the fence transport →
  direct host-path reads) with the wire form, the `exec_env`
  vocabulary and the caps unchanged — additive for the board; the
  fence-transport removal is an agent-machinery change, not a field
  change (§3.4c).
- **REMOVING a named field = MAJOR** (inherited); extending the
  per-harness table (a new harness, a new named field) — a minor change
  with committee notification; activating DEFERRED classes — a minor
  change of THIS contract with an owner gate (P1: adding a collected
  class is always gated); such an activation was executed by the
  discovery v8 amendment (AGW-27, 2026-10-29) for FC-8/FC-9.
- **Consumers**: the agent — obeys the catalog and the §3.3/§3.4/
  §3.4a/§3.4b forms; the board — ingest per the agent-discovery §3.11
  family + the §3.6
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
| **I**nformation Disclosure | identifying/credential-shaped content in the new FC-8/FC-9 strings (a tool version carrying a secret, a GPU serial, telemetry) | the version — the first line ≤200 runes through the names-only validator, drop-on-shape (§3.4a); GPU — names only ≤8, validator-gated, serials/utilization never (§3.4b); the §3.5 boundary | `tooling_version_discipline`, `compute_gpu_names_only` |
| **I**nformation Disclosure | the harness-configured probe as a channel to a foreign/credentialed endpoint | LOOPBACK only; `auth: configured` → never dialed; ≤8 targets; zero-redirect; one GET, quiet zero (§3.3.4; H3) | the probe-rule review (operational control) |
| **I**nformation Disclosure | container-home reads (v9 AGW-28 → v10 AGW-29) going beyond the named set: path-registry drift, whole files, files outside the table | reads follow the built-in table §3.3.2 ONLY — no second path registry (§3.4c); the 8 KiB read cap per file, ≤64 files per container home; fingerprint-discovered homes only, metal-wins dedupe (§3.4c); the pi marker — an existence-only stat; the §3.5 boundary applies to a container home as to ordinary host files, verbatim | `container_rows_shape`, `container_mcp_shape`, the walk-registry review (operational control) |
| **S**poofing | a foreign executor reports | the route's executor-token + identity-match (inherited; agent-discovery §3.1) | route integration tests (operational control) |
| **E**levation of Privilege | a discovery fact grants itself authority | advisory, never authority: the field creates no rows, extends no dictionaries (agent-discovery §3.1, §3.11) | board conformance (operational control) |
| **D**enial of Service | a bloated report (frontmatter ≤64 files × legs) chokes the board | shrink-to-fit (§3.3.5); the family's honest 422 (§4); the hourly cadence without its own timer | `row_caps`, `mcp_names_cap30` |
| **D**enial of Service | a bloated container-home walk (many boxes × many files) chokes the leg/board | the glob runs over discovery roots — fingerprint-discovered homes only (§3.4c); ≤64 files per home, the 8 KiB read cap; the `models`/`mcp_servers` caps surface-spanning/per-element + shrink-to-fit; quiet degradation when `.distrobox` is absent — the common case of hosts without boxes (§3.4c) | `row_caps`, `container_rows_shape` |
| **R**epudiation | «who dropped the row / who sent a credential?» | drops audited, incidents named, the local log loud (§3.3.6, §4) | operational control (the board's audit trail) |
| **T**ampering | the transparency rendering lies about the surface (catalog drift between the board's and the agent's contract versions) | the agent↔contract version handshake (§3.6); the field → FC map complete (§3.2); a field without an FC id = a defect | operational control (handshake tests) |

Conscious residual risks: a harness process reads its OWN configs — the
harness's threat model, not the fleet's (gate 2 §6); full board-host
compromise — outside the agent wire; MCP server names on the board —
advisory metadata of the same sensitivity as provider names; a
container home is an ordinary host directory — a planted
`.distrobox/<box>/home` passes the same fingerprint gating and the
same §3.5 boundary as metal homes, so the host-path read form grants
no additional privileges (§3.4c).

## 9. Migration and implementation status

The legacy leg: v6 (AGW-25) rides the wire — its standalone table is
superseded, but the field is compatible (§7). The legs' status —
honestly:

| Leg | Status | Where it lives |
|---|---|---|
| Agent v6 (standalone `models`) | **rode the wire** (AGW-25, merged 2026-10-28) — SUPERSEDED by this contract's population rules; zero rows on the real fleet (verified live 2026-10-28 on core-51: the four v6 config files are absent; the fleet's real harnesses — zcode/copilot — carry their catalogs in agent-definition frontmatter) | vesmaro/vesma-agent, main (merge b98960e); `docs/PROTOCOL.md` §3 |
| Agent v7 (per-harness re-key + FC-7) | **in flight** — the `feat/host-intake-contract` branch, AGW-26; the contract draft — `docs/design/host-intake-contract-draft.md` (this spec's source) | vesmaro/vesma-agent |
| Board mirror of the new fields (ingest of per-harness `models`, `mcp_servers`; the §3.6 transparency rendering) | **not merged** — a separate vesma-eyes wave (pending; contract §9) | vesma-eyes |
| FC-8 / FC-9 (tooling, compute) | **normative since discovery v8** (AGW-27, 2026-10-29; DEFERRED lifted by the owner's «делай» directive of 2026-10-29) — the normative text of this spec's §3.4a/§3.4b; the agent-side normative form — the «discovery v8 (AGW-27, 2026-10-29)» addendum in `docs/PROTOCOL.md` (landing in parallel with this amendment); FC-6/FC-7 container config surfaces — below (v9) | vesmaro/vesma-agent, `docs/PROTOCOL.md` |
| Agent v9/v10 (container-surface: FC-6/FC-7 from distrobox container homes, §3.4c) | **draft.4 shipped in the vesma v0.5.0 release with the fence transport; the owner's directive of 2026-10-29 (AGW-29) replaced the mechanism with DIRECT host-path reads** — this spec's normative text (draft.5); the fence transport is deprecated and removed from the agent; the agent-side normative form — the addendum in `docs/PROTOCOL.md` amending «Container-surface addendum — discovery v9» (landing in parallel); the v4 enter-based leg stays for binary/version probes; pod surfaces (`pod:<name>`) remain the follow-up wave | vesmaro/vesma-agent, `docs/PROTOCOL.md` |

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
(contract §10); (2a) the discovery v8 amendment (AGW-27, 2026-10-29):
FC-8/FC-9 (§3.4a/§3.4b) + the `discovery_models_catalogs` catalog knob —
this spec's normative text is ready, the agent-side form (the PROTOCOL
addendum) lands in parallel; (2b) the discovery v9 (AGW-28) and v10
(AGW-29, 2026-10-29) amendments: the container-surface §3.4c —
draft.4 (the fence transport) shipped in vesma v0.5.0; the owner's
architectural directive of 2026-10-29 («Не надо заходить в контейнер,
чтобы найти файлы его — все есть на хосте (как подключаемый том)!»)
replaced the mechanism with direct host-path reads — this spec's
normative text (draft.5) is ready, the PROTOCOL addendum (amending
the v9 addendum) lands in parallel, the fence transport is removed
from the agent; (3) the board
mirror wave — ingest + the
transparency rendering (including the additive `tooling`/`compute`
and the container rows);
(4) stable ratification — both sides' conformance green.
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
- The discovery v8 amendment (AGW-27, 2026-10-29) — the TC-pinned
  deltas the owner approved with «делай» on 2026-10-29: FC-8/FC-9
  un-deferred → normative (§3.4a/§3.4b), the `discovery_host_facts`
  knob for both, the `discovery_models_catalogs` catalog knob (§3.3.2),
  the §3.5 boundary extension; the agent-side normative form — the
  «discovery v8 (AGW-27, 2026-10-29)» addendum in vesma-agent's
  `docs/PROTOCOL.md`. The wave's spec-phase budgets (brief 2026-10-29):
  version-call timeout ≤2 s, the first version line ≤200 runes,
  `tools[]` ≤40, `gpus` ≤8, the 8 KiB read cap per catalog file (later
  raised to a DEDICATED 64 KiB for catalog entries — the vesma-agent
  v0.12.1 sync, §3.3.2), the
  `tooling`/`compute` fields at 8 KiB shrink-to-fit each.
- The discovery v9 amendment (AGW-28, 2026-10-29) — the TC-pinned
  deltas the owner approved with «делай» on 2026-10-29: the FC-6/FC-7
  «metal only» red line lifted for config reads through distrobox
  container probes (§3.4c; running containers only, the script
  generated from the SAME §3.3.2 table, per-file `head -c 8192` +
  base64 fenced blocks, ≤64 files per container home, the
  per-container budget inside the v4 30 s-leg/20 s-probe family —
  config-carrying up to 25 s of probe); per-surface row identity
  (§3.3.1) and surface-spanning caps (§3.3.5); FC-7 from containers —
  the entry-level detector (§3.4); the pi marker in a container —
  `test -f` existence-only (§3.3.2); quiet degradation without the
  distrobox CLI (§3.4c); knobs unchanged (`discovery_models` +
  `discovery_distrobox`); the §3.5 boundary extension (the
  container line); the agent-side normative form — the
  «Container-surface addendum — discovery v9 (AGW-28, 2026-10-29)»
  addendum in vesma-agent's `docs/PROTOCOL.md`. This amendment's
  MECHANISM (the fence transport) was replaced by discovery v10
  (AGW-29) — below; the per-surface row identity, the surface-spanning
  caps, the entry-level detector, the pi existence-only marker and the
  quiet degradation remain (§3.4c).
- The discovery v10 amendment (AGW-29, 2026-10-29) — the TC-pinned
  contract deltas (TL) under the owner's architectural directive of
  2026-10-29 «Не надо заходить в контейнер, чтобы найти файлы его —
  все есть на хосте (как подключаемый том)!» (do not enter the
  container to find its files — they are all on the host, like a
  mounted volume): §3.4c rewritten — DIRECT host-path reads of
  container homes (`<root>/.distrobox/<box>/home` — host-visible
  paths; a `<root>/.distrobox/*/home` glob per discovery root, pure
  stat; fingerprint gating as metal; metal-wins dedupe — a home path
  already covered by a metal root is not re-scanned, test-pinned; the
  same caps of ≤64 files/home and 8 KiB/file, the same decodes and
  validator; the pi existence-only marker; an absent `.distrobox` =
  quiet zero — the common case); the draft.4 fence transport (the
  vesma v0.5.0 release) deprecated and removed from the agent; the v4
  enter-based leg — binary/version probes only; the knob
  clarification: the container-home walk + the models/mcp reads ride
  `discovery_models`, `discovery_distrobox` gates only the v4 CLI
  leg; the §3.5 boundary extension; the agent-side normative form —
  the addendum in vesma-agent's `docs/PROTOCOL.md` amending
  «Container-surface addendum — discovery v9» (landing in parallel).
- The [glossary](../../../GLOSSARY.md), the
  [ecosystem map](../../../ECOSYSTEM.md), the
  [roadmap](../../../docs/roadmap.md).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) — keyword
  interpretation.
