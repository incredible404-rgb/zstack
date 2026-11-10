---
name: memory-routing
description: Which memory layer to search — Repository SSOT first, distilled cross-project memory (e.g. OpenViking) second, raw session transcripts (e.g. deja) third. Use whenever you are about to search past context, earlier decisions, prior errors, or hand off a long task across sessions.
---

Three sources, strict priority to eliminate hallucination and save tokens:

0. **Repository SSOT first (0 memory calls)** when working inside a tracked repo: current rules, script paths, schedules, and task states live in the repo (`AGENTS.md`, `ARCHITECTURE.md`, `GLOSSARY.md`, config manifests). Never trust recalled memories over current repo files.
1. **Distilled cross-project memory** (e.g. [OpenViking](https://github.com/volcengine/OpenViking) `viking://~/memories`, or a shared notes directory) for cross-project user preferences and durable entity/pattern cards:
   - Scope searches to the relevant subtree (e.g. `target_uri="viking://~/memories/preferences"`) or read the known URI directly when the topic name is already clear.
   - Start semantic `find` / `search` at `limit=5`: each hit carries its abstract, so larger defaults burn extra tokens. Raise it only when the hits miss the source you need.
   - Read the abstract rather than trusting raw cosine similarity scores (embedding scores often cluster tightly around 0.73–0.87 even for off-target hits).
   - For exact tokens *inside distilled notes*: use regex/grep tools (e.g. `openviking_grep`), not semantic `find`.
2. **Raw lossless transcripts** (e.g. `deja` CLI/MCP across agents, or local client session JSONLs under `~/.claude`, `~/.codex`, `~/.pi`) for exact historical evidence:
   - Exact strings: error messages (`deja fix "<error>"`), file edit history (`deja blame <path>`), CLI flags, commit SHAs, or what an agent actually ran/measured;
   - Rule/decision keywords: filter to assistant or user turns so always-injected `AGENTS.md` headers don't flood FTS results;
   - Keep full-text queries to 2–4 exact words.

Rules of thumb:
- *Current project rule or path* → Repo SSOT.
- *User taste, personal preference, cross-project convention, or "why we chose X"* → Distilled memory.
- *Exact error string, command output, or file edit history* → Raw session transcripts.
- Each external memory lookup costs ~1–3 s; never wire semantic memory or full transcript scans into synchronous per-prompt shell hooks.

## Continuing long tasks across sessions/agents (Kanban handoff)

- Before resuming a multi-session task from another session or agent, check your shared kanban directory (e.g. `viking://~/resources/kanban/` or `.agents/kanban/`) for its card and reuse it.
- Record four fields only: **goal (What)**, **constraints**, **verified progress (with command/commit proof)**, and **next step**. Write back and verify after real progress, at handoff, and before context compaction.
- Short Q&A with no follow-up gets no card; never pick up another active session's card on your own.
- One task, one writer — an owner field is metadata, not a mutex. Never store credentials, raw secrets, or giant tool dumps in handoff cards.
