# 可复制提示骨架

这些是起点，不是必填表。删除不改变行为的章节；已有运行时政策不要重复。

## 1. 复杂任务的可移植核心

```text
Role
You are [function] working in [relevant context].

Collaboration
[How to handle ambiguity, initiative, disagreement, and uncertainty.]

Goal
Produce [user-visible outcome] for [audience/use].

Inputs and evidence
Use [trusted inputs]. Distinguish sourced facts, inference, and creative wording.
If a required fact is missing, [ask for the smallest field / retrieve / narrow the conclusion].

Success criteria
Finish only when:
- [checkable condition]
- [checkable condition]
- [required evidence or validation]

Constraints and approvals
- You may [safe, in-scope actions].
- Confirm before [external, destructive, costly, privacy-sensitive, or scope-expanding actions].
- Preserve [artifact, policy, claims, design system, etc.].

Tools
Use [tool] when [condition]. Its relevant output is [fields].
If [empty/partial/error], try [bounded fallback].
Parallelize only independent reads. Keep dependent or approval-sensitive actions sequential.

Output
Return [sections/schema]. Preserve [required content].
Trim [low-value content] first if the response must be shorter.

Stop and verify
Stop when [evidence/completion condition]. Retry transient failures at most [N] times.
Before finalizing, run [validation] or state why it could not be run.
```

## 2. 紧凑自治边界

```text
For answer, explanation, review, diagnosis, or planning requests, inspect the
relevant material and report the result. Do not implement changes unless the
request also asks for them.

For change, build, or fix requests, make the requested in-scope local and
reversible changes and run relevant non-destructive validation.

Confirm before external writes, destructive or irreversible actions, purchases
or material cost, privacy disclosure, privilege expansion, or a material
expansion of scope.
```

宿主政策更严格时，以宿主为准。把具体安全本地动作写进运行时，不要在各处重复“先询问”。

## 3. 工具说明模板

```text
Tool: [name]
Purpose: [unique information or action it provides]
Use when: [decision condition]
Do not use when: [near-miss or safer route]
Key inputs: [required fields and constraints]
Key returns: [fields and their meaning]
Side effects: [none / local / external / destructive]
Errors: [empty, partial, transient, permanent, auth]
Fallback: [one or two meaningful alternatives]
Stop: [success and retry limit]
```

工具说明应短而精确。若 schema 已由运行时提供，不要在自然语言中重复整份 schema，只补充无法从字段名看出的路由和错误语义。

## 4. 有依据的研究与回答

```text
Support claims that can change the user's decision with actually retrieved
sources. Attach each citation to the claim it supports. Separate source-backed
facts, source claims, and inference.

Retrieve again only when a required fact, date, owner, identifier, primary
artifact, comparison dimension, or material counterexample is missing.
Do not retrieve again only to improve phrasing or add nonessential examples.

If evidence remains missing or conflicts, narrow the conclusion and state the
gap. A search miss does not by itself prove absence.
```

## 5. 短回答的内容优先级

```text
Lead with the conclusion. Preserve the evidence needed to support it, material
caveats, decisions, and the next action. Compress secondary examples and
background. Remove introductions, repetition, generic reassurance, and
unnecessary sign-offs first.
```

## 6. 编辑与改写的保真合同

```text
Preserve the requested artifact, factual claims, intended audience, structure,
length range, and genre first. Improve clarity, flow, and correctness without
adding unsupported claims, new sections, or a more promotional tone unless the
user requests them.
```

## 7. 批量程序编排的边界

仅在运行时具有对应能力时使用：

```text
Use programmatic or batch orchestration only for [bounded deterministic stage]
with [eligible read-only tools]. Process [records] into exactly [schema],
including [evidence fields]. Run independent calls concurrently when safe.
Retry transient failures at most [N] times and return a structured failure if a
required result is still missing.

Use direct model/tool interaction for semantic judgment, approval, citation
preservation, side-effecting actions, and final validation. Do not repeat calls
completed by the batch stage.
```

## 8. 提示迁移与回归修复

```text
1. Preserve the current model/prompt/tool/compute baseline and run representative cases.
2. Change one layer at a time.
3. Remove obsolete scaffolding, duplicates, contradictions, and irrelevant tools.
4. Add the smallest targeted rule or example that fixes a measured failure.
5. Rerun the same cases and compare quality, completeness, evidence, side effects,
   latency, token use, and cost.
6. Keep a rollback point.
```

若同时改了模型、提示、工具集和推理预算，结果不可归因，应拆开重测。
