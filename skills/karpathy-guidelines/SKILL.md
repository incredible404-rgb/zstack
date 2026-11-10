---
name: karpathy-guidelines
description: Behavioral guidelines for non-trivial coding, debugging, code review, refactoring, or architecture work. Use to surface assumptions and tradeoffs, avoid overcomplication, keep changes surgical, and define verifiable success criteria. Apply lightly to trivial typo fixes or obvious one-line changes.
license: MIT
compatibility: no external tools or network access required.
metadata:
  upstream: multica-ai/andrej-karpathy-skills
  upstream-version: 1.0.0
---

# Karpathy Guidelines

Behavioral guidelines to reduce common LLM coding mistakes, derived from [Andrej Karpathy's observations](https://x.com/karpathy/status/2015883857489522876) on LLM coding pitfalls.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## How to apply

For a non-trivial task, briefly identify assumptions, the smallest sufficient approach, the intended edit boundary, and a concrete verification step before implementation. Ask a clarifying question only when unresolved ambiguity could materially change the result. Do not turn these guidelines into ceremony for obvious, low-risk changes.

When a concrete before/after example would clarify a principle, read [`references/EXAMPLES.md`](./references/EXAMPLES.md).

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them; don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it; don't delete it.

When your changes create orphans:
- Remove imports, variables, or functions that your changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria such as "make it work" require repeated clarification.

---

**These guidelines are working if:** diffs contain fewer unnecessary changes, first implementations need fewer complexity-driven rewrites, and material ambiguities are clarified before implementation rather than after mistakes.
