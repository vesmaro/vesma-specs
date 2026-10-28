# Agent Discovery v0 — Quickstart

Agent discovery v0 is the wire contract for the `models` field — the
additive top-level field the outbound ЦУП agent (`vesmaro-agent`) adds
to its hourly discovery report
`POST /api/executors/{executor_id}/discovery`. It tells the board which
providers and models are actually configured on the executor's host —
**names only**: provider/model names and endpoint URLs are facts;
credential material is never read, never emitted, in any encoding.

Status: **draft** (`0.1.0-draft`). The agent leg is already merged as
protocol amendment AGW-25 (vesma-agent, main (merge b98960e)); the
board mirror (ingest into `GET /api/models`) is the next vesma-eyes
wave.

## Normative spec

[spec.md](spec.md) — the normative contract (Russian canon, RFC 2119).

English mirror: [spec.en.md](spec.en.md) (informative; the Russian text
governs).

## What an agent MUST do (summary)

1. **Read nothing but named fields.** A built-in per-harness layout
   table names, per config file, exactly the fields read
   (JSON-pointer / section-path level). Scan heuristics are forbidden.
   Since the draft.2 re-key the table's population norm is
   [host-intake §3.3.2](../../host-intake/v0/spec.md): zcode/copilot
   agent frontmatter (`model:`/`tier:`), codex, continue, claude-code,
   aider, and the pi auth-marker row (the v6 standalone list below is
   superseded).
2. **Never touch credential values.** `auth` is an enum fact —
   `configured | anonymous | unknown` — derived ONLY from the presence
   of the marker fields the table names.
3. **Normalize `base_url`** to `scheme://authority[/base-path]`; query,
   fragment and userinfo are ALWAYS stripped; a credential-shaped query
   parameter (`?key=…`) means host-only redaction or omission.
4. **Respect the caps, shrink before send**: `provider` ≤ 60 chars,
   `models[]` ≤ 50 sorted, `installations[]` ≤ 64 rows, the whole
   `models` object ≤ 16 KiB, an 8 KiB read cap per config file; an
   oversize/unparsable file is an honest absence, truncation rides the
   row's `note`.
5. **Probe anonymously, loopback only**: a fixed port table (ollama
   11434 `/api/tags`; LM Studio 1234, llama.cpp 8080, vLLM 8000 —
   `/v1/models`), one GET, 2 s timeout, no credentials; failure is a
   quiet zero.
6. **Drop on leak suspicion**: a credential-shaped string in an
   unexpected field drops the whole row before marshal, with a loud
   local log whose reason never carries the value. The agent emits no
   events — `models.credential_leak_suspected` is board-side.
7. **Honour the knob**: `discovery_models: auto|off` (default `auto`;
   unknown values refused at startup). Off = the field is absent
   entirely; ran = present even when empty (a real zero-and-ran).

## What a board MUST do (summary)

- Accept-and-ignore: a board that ignores `models` stays correct (the
  additive unknown-field rule); a pre-1.38 board is met with the
  agent's 404-silence.
- Ingest: unknown `harness`/`exec_env` → row dropped + audited
  (`discovery.rejected`); unknown `provider` names stored advisory;
  caps enforced honestly (`422`, never a silent trim); a
  credential-shaped string in an unexpected field → drop + the
  `models.credential_leak_suspected` incident event.
- Mirror: last report wins; identical re-report is a no-op; absent
  field ≠ empty field (no-wipe).

## Wire shape

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

Worked examples: [examples/](examples/) — a `config`-source row, a
`probe`-source row, and a credential-redaction before/after.

## How to verify

- Conformance suite: `conformance/cases.skeleton.yaml` (declarative
  skeleton — the runner is a single component-manifest profile today;
  executing this vocabulary is a runner-profile wave; the machine
  schema lands with the board mirror); check vocabulary in the spec §6.
- Integrator checklist: `conformance/checklist.md`.

## Sibling documents

[ADR-0002](../../../adrs/0002-agent-discovery-contract.md) (why this
contract exists and its authority trail),
[GLOSSARY.md](../../../GLOSSARY.md) (provider/model/installation in the
fleet sense),
[ECOSYSTEM.md](../../../ECOSYSTEM.md) (component statuses).
