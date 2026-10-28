# ADR-0003: the explicit collection catalog as the host-intake v0 contract

- **Status**: accepted
- **Date**: 2026-10-28
- **Deciders**: the owner directive 2026-10-28 — two clauses (the
  per-harness models re-key; the explicit collection-surface contract) —
  authorized the contract and its gate decisions (FC-6+FC-7 this wave;
  FC-8/9 — DEFERRED to v2; the loopback probe approved; dual-form
  emission approved); the TL brief — the spec wave's scope and
  structure; the text-authority parties — the agent-side contract draft
  (vesma-agent, feat/host-intake-contract) and the carried
  security-verdict red lines (832cd7a)
- **RU canon**: [0003-host-intake-catalog.md](0003-host-intake-catalog.md)
  — this is an informative translation; the Russian version governs

## Context

Clause 1 of the owner directive 2026-10-28 exposed a defect of the v6
leg (AGW-25): the standalone models table looked for configs detached
from the inventory and produced ZERO rows on the real fleet — verified
live 2026-10-28 on core-51: the four v6 config files do not exist, while
zcode/copilot — the harnesses the agent actually finds — carry their
model catalogs in agent-definition frontmatter (the fleet `models.yaml`
rendered by the GCW installer). The v6 design is superseded; its red
lines and disciplines carry forward verbatim.

Clause 2 of the same directive raised the bar: the agent's collection
surface must be an EXPLICIT contract — every fact class the agent
gathers on a host is enumerated; this is simultaneously the user-trust
surface (the owner sees the complete "what does the agent collect" list)
and the completeness bar (the fleet gets the maximum useful fact volume
within those limits). Until now, "what the agent collects" lived
scattered across protocol addenda (v1–v6) and was neither complete, nor
diffable, nor presentable to the user.

The agent-side contract draft
(`docs/design/host-intake-contract-draft.md`, vesma-agent,
feat/host-intake-contract) fixed the FC-1…FC-9 catalog, the P1–P6
principles and the open questions OQ-1…OQ-5; the draft's gates are
owner-approved: FC-6+FC-7 in the first wave, FC-8/FC-9 DEFERRED to v2,
the loopback probe (including harness-configured base_urls) approved,
dual-form emission approved.

## Decision

1. **Open the contract `specs/host-intake/v0/`** (`0.1.0-draft`, status
   draft): RU canon + EN mirror + EN quickstart + examples + a
   conformance skeleton + a CHANGELOG, per the full spec-template
   skeleton (ADR-0001 §1).
2. **The catalog = the trust/transparency surface.** §3.2 of the spec is
   a closed list of fact classes; anything not named is not collected;
   adding a class = an amendment with an owner gate (P1). Every wire
   field maps to exactly one FC id; the board renders "what agents
   collect" FROM the contract text, via the version handshake (P6).
3. **FC-6 is normative in host-intake**: the per-harness re-key (rows
   only for discovered harnesses — structural), the per-harness layout
   table (zcode/copilot frontmatter `model:`/`tier:` — grounded
   2026-10-28; codex/continue/claude-code/aider — v6 carried; pi — the
   auth-marker provider `pi` row with an empty `models[]`; gemini/qwen —
   absent), the documented provider string forms (dual-form emission,
   never guess), the probe: the fixed loopback table + ≤8
   harness-configured base_urls (anonymous, never credentialed — the H3
   verdict), the v6 red lines verbatim.
4. **FC-7 is normative in host-intake**: the additive top-level
   `mcp_servers` element — `{harness, exec_env, servers[] ≤30 sorted,
   count = the full total}`; names + transport kind from documented
   caches/configs; pi `mcp-cache.json` — names only (values never
   decoded); the `discovery_models` knob shared with FC-6.
5. **FC-8/FC-9 — catalogued, DEFERRED (v2)**: the owner's decision is
   recorded; implementation is a separate class wave; activation = a
   minor of host-intake with a gate.
6. **`sessions[]` — outside the agent's surface**: the discovery
   report's field is fed by the board's eyes-side scanner (ME-062; the
   kora-scan ingest; the synthetic executor id `hermes`); the agent
   constructs no session facts (verified 2026-10-28 in the agent's and
   the board's code); the spec records this honest absence (P4).
7. **The agent-discovery amendment to 0.1.0-draft.2**: the re-key of the
   `models` field's population (the standalone table superseded), the
   probe extension, the FC-7 element; the §3.2 row form and the §3.11
   board duties unchanged — the wire is additive, old boards conformant.
   The released contract version is not renumbered: draft.2 within the
   draft status.
8. **The waves**: the spec (this one) → the agent wave v7 (AGW-26,
   feat/host-intake-contract: the re-key + FC-7, release v0.11.0, the
   fleet update) → the board mirror wave of vesma-eyes (ingest + the
   transparency rendering).

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep "what the agent collects" in PROTOCOL.md addenda | the surface crosses components (agent → board → user-facing rendering) and must be public, versioned and diffable; the layer rule "HOW they connect → specs" (ADR-0001) directly demands the home here; addenda are history, not a living norm |
| An implicit surface + retrospective code audits | violates clause 2 of the directive: without an explicit list the owner cannot see the complete collection list, and "audit the code" does not scale and is not presentable to the user; the explicit catalog makes code-vs-catalog drift observable through the transparency rendering |
| Collect FC-8/FC-9 in the first wave | the owner's decision at the draft gate — deferred: the value is real (roster/ml-routing honesty), but the wave already carries the core re-key + a new leg; cataloguing without activation sets the v2 bar without the wave's risk |
| Extend the v6 standalone table with new harnesses | treats the symptom, not the disease: a table detached from the inventory again produces rows where the harness is not discovered and zero where the catalog lives in frontmatter; the per-harness re-key makes the impossible impossible by construction |

## Consequences

**Positive.** The collection surface gained an ecosystem home: the
complete public "what agents collect" list, FC-id cards for the board's
rendering, per-release diffability; the v6 zero rows are replaced by a
grounded per-harness population; FC-7 gives the fleet an honest
MCP-server audit (routing and inventory without any content); the v7
wave receives a finished spec instead of reverse engineering.

**Obligations.** The agent must keep the code in exact correspondence
with the catalog (drift = a defect, visible through the field → FC map);
extending the per-harness table and activating DEFERRED classes — minor
changes with tracing; removing a named field — MAJOR. The board mirror
wave must implement the transparency rendering from the contract text
with the version handshake — otherwise P6 stays a paper bar.

**Return point.** If the owner changes the FC-8/FC-9 decision or the
catalog's boundaries — the changes enter through host-intake's SemVer
process (an owner gate on every added class), not a silent rewrite.

## References

- [specs/host-intake/v0/spec.md](../specs/host-intake/v0/spec.md) —
  the codified contract (RU canon)
- The owner directive 2026-10-28 — two clauses (the decision's
  authority)
- The agent-side contract draft —
  `docs/design/host-intake-contract-draft.md` (vesmaro/vesma-agent, the
  `feat/host-intake-contract` branch): the catalog, the P1–P6
  principles, the gates OQ-1…OQ-5 (owner-approved)
- Gate 2 — `docs/design/models-fleet/security-verdict.md`
  (vesmaro/vesma-eyes, `feat/models-fleet-blueprint`, 832cd7a) — the
  carried red lines (names-only, URL normalization, auth-from-presence,
  H3, the board detector)
- [specs/agent-discovery/v0/spec.md](../specs/agent-discovery/v0/spec.md)
  (0.1.0-draft.2) — the `models` field's wire discipline (the row form,
  the board duties) and its re-key amendment
- [ADR-0002](0002-agent-discovery-contract.md) — the predecessor (the
  agent-discovery codification)
- ME-062 / kora-scan / `KORA_HERMES_EXECUTOR_ID` — vesma-eyes
  `server/app.py`: the scanner-owned `sessions[]` leg (the evidence for
  decision 6)
- [ADR-0001](0001-repo-structure-and-governance.md) — the layer's
  structure and governance
- [ECOSYSTEM.md](../ECOSYSTEM.md), [GLOSSARY.md](../GLOSSARY.md) — the
  map and the glossary
