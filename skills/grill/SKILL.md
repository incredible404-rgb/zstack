---
name: grill
description: Grill the user about a plan, decision, or idea, three questions a round. Use when the user wants their thinking stress-tested, or wants to be questioned before work starts so the requirements get pinned down (grill me、拷问我、追问我、问我几个问题、帮我把方案想清楚、先问清楚再做).
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Every node is a **What** or a **How**. A What is what the user wants and how they will know they got it: the outcome, the **proof** that will show it is done, the constraints, what is out of scope, the limit on time or cost. A How is the route there: tools, structure, order of steps. Grill the Whats. Settle the Hows yourself from the facts you can find; they surface once, in the closing How sketch, never as questions. A How becomes a question only when it touches the owner's domain (see `owner-mode` or the Owner's Domain list in global instructions) or cannot be undone.

When the user hands you a How ("use X", "do A, then B"), ask for the What behind it: what is X meant to secure? Keep the How as a constraint when a real reason stands behind it (an outside requirement, a past failure, a preference they hold); otherwise record the outcome and free the route.

Push each What until it is observable: "better", "faster", "clean" becomes a number, a before/after, a check someone else could run. Proof sits on the first round's frontier: _when this is done, what will you look at to believe it?_

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask **three** frontier questions a round (fewer only when the frontier holds fewer), picking the ones whose answers unblock the most downstream decisions; the rest of the frontier waits for a later round. Number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer. A question the user's reply leaves unanswered takes your recommended answer: close each round with one line saying so.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, runtime behavior, etc.), dispatch a sub-agent with a fresh context window to find or test it; don't ask the user for anything you could look up or run yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask other frontier questions now. The _Whats_ are the user's: put each to them and wait.

Inside a project repository, **record** each answer the moment it settles; recording is part of the session, not acting on the plan. A resolved term goes into the project's glossary (whatever its AGENTS.md or README names, e.g. `GLOSSARY.md`, `术语表.md`), in that file's own format; with no glossary, terms stay in the conversation. A decision that is hard to reverse or surprising without context goes into the project doc that owns that area, as current state plus the reason, rewriting the entry it supersedes. Outside a repository, everything stays in the conversation.

The session is done when the frontier is empty: every What settled, nothing left silently assumed. Close with a **brief** in two parts. First the Whats: outcome, proof, constraints, out of scope, limit. Then the **How sketch**: the route you would take, its key choices and where it is risky, one line each, so the user can glance at it and veto any line; a vetoed line becomes a What and goes back on the frontier. Write the brief so the work that follows takes it whole: the Whats as the goal (the client's native goal when it has one, e.g. `/goal` or a Codex goal), the How sketch as the plan's opening, revised in the open if the route changes. Do not act on it until the user confirms you have reached a shared understanding. That confirmation is also the goal sign-off the global goal rule asks for; do not ask again before starting.
