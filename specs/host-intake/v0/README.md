# Host Intake v0 — Quickstart

Host intake v0 is the **explicit collection catalog**: the complete list
of fact classes (FC-1…FC-9) the outbound ЦУП agent (`vesmaro-agent`) may
gather on a host, plus the normative wire forms of the two legs this
wave touches — FC-6 (models keyed to discovered harnesses) and FC-7
(MCP server names). Anything not named in the catalog is not collected.
This is the fleet's trust and transparency surface: the complete "what
agents collect" list is public, versioned and diffable per release.

Status: **draft** (`0.1.0-draft`). Authority: owner directive
2026-10-28 (two clauses: the per-harness models re-key + the explicit
collection contract); the agent-side contract draft
(`docs/design/host-intake-contract-draft.md`, vesma-agent
`feat/host-intake-contract`) with owner-approved gates; the carried
fleet security-verdict red lines (832cd7a). The agent v7 wave (AGW-26)
is in flight; the board mirror wave is pending.

## Normative spec

[spec.md](spec.md) — the normative contract (Russian canon, RFC 2119).

English mirror: [spec.en.md](spec.en.md) (informative; the Russian text
governs).

## What an agent MUST do (summary)

1. **Collect only catalogued classes** (P1). The catalog §3.2 is closed:
   FC-1…FC-7 live/approved, FC-8/FC-9 DEFERRED to v2 (not collected
   until a gated activation).
2. **Respect the never-collected boundary** (P2/P3, §3.5): file contents
   (outside the named exceptions), project/workspace names, prompts and
   session content, env VALUES, network traffic, credential material —
   never.
3. **Attribute per harness, structurally** (FC-6/FC-7): a row exists
   only for a harness the inventory actually discovered; the scan runs
   over the inventory results. The v6 standalone table is superseded.
4. **Read configs through the per-harness layout table only**
   (§3.3.2): zcode/copilot agent frontmatter (`model:`/`tier:`,
   ≤64 files, 8 KiB/file), codex TOML, continue JSON, claude-code
   settings, aider YAML, pi `auth.json` existence marker. gemini/qwen —
   no rows. Scan heuristics are forbidden.
5. **Emit dual forms, never guess** (§3.3.3): raw model strings in
   `models[]`; the parsed provider in the row's `provider` — only via a
   documented form (`(provider)` suffix, `provider/model` prefix, the
   literal `(copilot)` vendor form); otherwise the harness bucket with a
   note. `base_url` omitted when the source names no endpoint.
6. **Probe anonymously, loopback only** (§3.3.4): the fixed v6 port
   table plus ≤8 harness-configured loopback base_urls — anonymous only,
   never credentialed, never non-loopback, zero-redirect, quiet zero.
7. **Carry the v6 red lines verbatim** (§3.3.6): the names-only
   validator (drop, never mangle), `base_url` normalization, auth from
   field presence only, row drop before marshal + loud log on leak
   suspicion, no agent-side events, `exec_env: metal`.
8. **Report MCP server names only** (FC-7, §3.4): the additive top-level
   `mcp_servers` field — `{harness, exec_env, servers[] ≤30 sorted,
   count = full total}`; pi `mcp-cache.json` keys as names, values never
   decoded; governed by the same `discovery_models: auto|off` knob.

## What a board MUST do (summary)

- Ingest the additive fields per the agent-discovery §3.11 family:
  unknown `harness`/`exec_env` → drop + audit; honest 422 on caps.
- Render the static "what agents collect" view FROM this contract, one
  card per FC id, pinned to the agent's contract version via the version
  handshake (§3.6).
- Treat `sessions[]` as scanner-owned: it is fed by the eyes-side
  scanner (kora scan / the synthetic `hermes` executor), not by the
  agent (§1, §9).

## Wire shapes

```json
{"models": {"installations": [
  {"provider": "ollama-cloud",
   "auth": "unknown",
   "models": ["GLM 5.3 Flash (ollama-cloud)",
              "ollama-cloud/glm-5.3-flash"],
   "harness": "zcode",
   "exec_env": "metal",
   "source": "config",
   "note": "provider parsed from the documented (provider) suffix form; default model of harness zcode"}]}}

{"mcp_servers": [{"harness": "pi", "exec_env": "metal",
  "servers": ["context7", "playwright"], "count": 5}]}
```

Worked examples: [examples/](examples/) — a zcode frontmatter row, the
pi auth-marker row, the `mcp_servers` field, and a credential-redaction
before/after.

## How to verify

- Conformance suite: `conformance/cases.skeleton.yaml` (declarative
  skeleton — the runner is a single component-manifest profile today;
  executing this vocabulary is a runner-profile wave); check vocabulary
  in the spec §6.
- Integrator checklist: `conformance/checklist.md`.

## Sibling documents

[ADR-0003](../../../adrs/0003-host-intake-catalog.md) (why the explicit
catalog exists — the trust/transparency decision),
[agent-discovery v0](../../agent-discovery/v0/README.md) (the `models`
field's wire discipline this contract populates),
[GLOSSARY.md](../../../GLOSSARY.md),
[ECOSYSTEM.md](../../../ECOSYSTEM.md).
