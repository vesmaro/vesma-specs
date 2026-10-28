# ADR-0002: codifying the model discovery wire as the agent-discovery v0 contract

- **Status**: accepted
- **Date**: 2026-10-28
- **Deciders**: the owner directive of 2026-10-28 («update the contracts
  and documentation» in vesma-specs) sanctioned the codification; the TL
  brief fixed the scope and structure; the authority parties are the
  three ratified models-fleet gates (vesma-eyes) and protocol amendment
  AGW-25 (vesma-agent)
- **Canonical text**: [0002-agent-discovery-contract.md](0002-agent-discovery-contract.md)
  — Russian canon; this file is an informative translation

## Context

The model discovery wire — the additive `models` field of the
`POST /api/executors/{executor_id}/discovery` route — lived until
2026-10-28 ONLY in the agent repo: as the «Models-fleet addendum —
discovery v6 (AGW-25, 2026-10-28)» addendum in `docs/PROTOCOL.md` §3 of
vesma-agent. For the ecosystem this is a gap: the wire crosses a
component boundary (agent → the `vesma-eyes` board), and the layer rule
therefore demands a home in vesma-specs («HOW they connect → specs» —
ADR-0001).

Meanwhile the «providers and models as a fleet» epic (owner dictation
2026-10-23) produced and ratified three gates in vesma-eyes (the
`feat/models-fleet-blueprint` branch):

1. **gate 1** — `discovery-contract-draft.md` (daf969b): wire shape,
   red lines §2.2, trust boundaries §4;
2. **gate 2** — `security-verdict.md` (832cd7a): the OQ-4 verdict on
   names-only config reads with amendments 1–2 (structural bounding by
   the layout table instead of grep; stripping query/fragment and
   credential parameters from `base_url`), the H1–H4 verdicts (storage,
   pull proxy, anonymous probe, audit), the final red lines §4;
3. **gate 3** — `ux-blueprint.md` (cb166a8): the mirror consumers
   (MF1/MF2, `GET /api/models`).

The agent leg is already merged into the agent's protocol (AGW-25) and
rides the wire; the board mirror (ingest into `GET /api/models`, the
`discovered` zone) is not merged yet — the target `ModelsDiscoveredItem`
schema is already served by the board, the zone stays honestly empty.

## Decision

1. **Open the contract `specs/agent-discovery/v0/`** (`0.1.0-draft`,
   status draft): RU canon + EN mirror + EN quickstart + examples +
   conformance skeleton + CHANGELOG, per the full spec-template
   skeleton (ADR-0001 §1).
2. **Authority trail**: every normative requirement of the spec traces
   to AGW-25 or gates 1–2; the spec invents nothing beyond them. The
   authority parties are recorded in the spec's status header and its
   CHANGELOG.
3. **Scope — the agent → board wire only**: field form, read red lines,
   caps, the probe leg, leak discipline, snapshot semantics, board
   ingest duties, error codes. Credential storage, sharing grants and
   the pull proxy are out of scope (gate 2's verdict domain in
   vesma-eyes); roster UX is out of scope (gate 3's domain). The
   contract must stay correct if the owner answers the proxy «never»
   (gate 1 §4.5, gate 2 §4.10).
4. **Dependency**: stable ratification waits for the green conformance
   of both legs; the next implementer is the vesma-eyes board mirror
   wave (the spec's §3.11 ingest). Intermediate states (one leg live,
   the other not) are conformant by the additive rule — no wave order
   is imposed.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep the contract only in the agent's PROTOCOL.md | the wire crosses components: the board mirror and third-party integrators read the spec layer, not the agent protocol; the layer rule «HOW they connect → specs» (ADR-0001) explicitly demands a home here |
| Codify after the board mirror lands | the agent leg already rides the wire: a contract should describe living reality, and the additive rule makes intermediate states safe — deferring means codifying post factum for no reason |
| Rewrite the gates into the spec as a new norm | the gates are ratified in vesma-eyes with their own context; the spec codifies them with tracing instead of re-litigating — divergence will be caught by review against the gates' SHAs |

## Consequences

**Positive.** The model discovery wire gained an ecosystem home with
examples, a conformance vocabulary and an honest implementation-status
section; the board wave receives a ready ingest specification (§3.11,
no-wipe §3.10, honest 422 §4) instead of reverse-engineering the
addendum.

**Obligations.** Layout-table extension is a minor contract change
traced into the AGW registry; removing a named field is MAJOR (spec §7).
The machine JSON-Schema and the executable suite land together with the
board mirror. An open question for the mirror wave: the dictionary
membership of probe slugs (a probe row's `harness` carries the probe
source's name, e.g. `ollama`) — decided consciously, not by a silent
carve-out (spec §3.2, §3.11).

**Return point.** If the vesma-eyes gate documents change the red lines
after the spec is ratified — changes enter through the spec's SemVer
process, never by silently rewriting the trace.

## References

- [specs/agent-discovery/v0/spec.md](../specs/agent-discovery/v0/spec.md)
  — the codified contract (RU canon)
- `docs/PROTOCOL.md` §3 (AGW-25) and §7.1 — vesmaro/vesma-agent, the
  main (merge b98960e) branch — the agent leg's normative source
- Gate 1: `discovery-contract-draft.md` (daf969b), gate 2:
  `security-verdict.md` (832cd7a), gate 3: `ux-blueprint.md`
  (cb166a8) — vesmaro/vesma-eyes, the `feat/models-fleet-blueprint`
  branch
- `ModelsDiscoveredItem` / `ModelsRosterOut` — vesma-eyes
  `server/app.py` (the `discovered` zone, the MF2 cut)
- [ADR-0001](0001-repo-structure-and-governance.md) — the layer's
  structure and governance
- [ECOSYSTEM.md](../ECOSYSTEM.md), [GLOSSARY.md](../GLOSSARY.md) — the
  map and the glossary
