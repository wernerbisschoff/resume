---
title: "DeviaTDD's SDD layers: claims, ledgers, and merges"

publishDate: 2026-07-15T00:00:00Z
draft: false
excerpt: 'DeviaTDD keeps Product, Macro, and Meso work legible by turning an issue claim into a branch, recording transitions in append-only JSONL, and merging those records as a union.'
category: DeviaTDD
tags:
  - deviatdd
  - spec-driven-development
  - agent-orchestration
  - git
author: Werner Bisschoff
metadata:
  description: 'DeviaTDD keeps Product, Macro, and Meso work legible by turning an issue claim into a branch, recording transitions in append-only JSONL, and merging those records as a union.'
---

In an [earlier note](/notes/deviatdd-micro-tdd-loop/) I described the micro loop — what happens when one agent runs Red → Green → Judge → Refactor on a single task. This post is about the layers above it. I build this for the moment after a long agent run when I need one boring answer: which issue owns this branch, and which line proves it?

DeviaTDD calls the whole shape a Four-Layer Architecture: Product, Macro, Meso, Micro ([`specs/constitution.md:8-15`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/specs/constitution.md#L8-L15)). The first three are the SDD stack. The micro layer is the TDD sandbox; see the [micro-loop post](/notes/deviatdd-micro-tdd-loop/) for that executable-code cycle. Here the artifacts are plans, specs, tasks, and ledger rows.

## Three SDD layers

**Product → flows → architecture → release.** Product is optional for a single-feature repository. When it exists, it keeps cross-product intent in view before a feature is sliced. The constitution puts this layer first and gives it a gate: design approval after research. No layer is silently skipped; Product is the explicit exception for a one-feature repo.

**Macro → explore → research → PRD → shard + specify.** Macro turns a product-shaped problem into feature-sized contracts. Explore gathers the surface area; Research tests the design; the PRD makes the contract concrete; Shard + Specify turns it into issues that Meso can claim. Its output is still specification, not production code.

**Meso → plan → tasks.** Meso is where an issue becomes executable work. Plan names the approach and constraints; Tasks make the work schedulable. The branch is not an afterthought here. It is the claim receipt: a durable answer to “who is working on this issue?”

Every layer has a human checkpoint. The constitution names three mandatory HITL gates — design approval, contract sign-off, and final merge audit — and says none may be bypassed ([`specs/constitution.md:13`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/specs/constitution.md#L13)). The layers are therefore `intent → contract → issue → task → code`, with a person still deciding at the joins.

## Branches are claims

The branch convention is not cosmetic: `feat/<epic-slug>/<issue-slug>` ([`specs/constitution.md:67`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/specs/constitution.md#L67)). In the claim path, `meso.py` derives that exact name at line 495:

```python
branch = f"feat/{epic_slug}/{issue_slug}"
```

The important call graph is:

```text
_specify_pre (meso.py:632)
  → resolve_issue_record (meso.py:641)
  → _try_claim_issue
      → create_worktree
      → claim_issue(... specs/issues.jsonl)
      → commit + push the claim
```

`_specify_pre` is the entry point, not `feature.py`: it resolves the issue and calls `_try_claim_issue` ([`src/deviate/cli/meso.py:632-656`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/cli/meso.py#L632-L656)). `_try_claim_issue` creates the worktree and writes the `SPECIFIED` transition through `claim_issue` before committing and pushing it ([`src/deviate/cli/meso.py:511-540`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/cli/meso.py#L511-L540)).

| Evidence                                | What it establishes                                                                                                                                                                                                                                               |
| --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/deviate/cli/meso.py::_specify_pre` | Issues the claim, creates the worktree, and writes the status transition. Git Isolation is enforced from `feature.py:28-34`: micro-layer agents never run `git checkout -b`.                                                                                      |
| `src/deviate/cli/feature.py:28-34`      | The feature CLI's `_create_feature_branch` docstring says branch creation is the only sanctioned entry point and TDD agents must not mutate branch state ([source](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/cli/feature.py#L28-L34)). |
| `specs/constitution.md:67`              | The branch name carries epic and issue identity.                                                                                                                                                                                                                  |

That distinction matters. A branch created by a random agent is merely a ref. A branch issued by Meso is a claim with a worktree, a ledger transition, and a commit behind it. `feat/epic/issue` is a small protocol, not a naming preference.

## Append-only JSONL, then merge = union

The constitution makes the storage rule blunt: `issues.jsonl`, `tasks.jsonl`, and `flows.jsonl` are append-only; canonical state is derived by sequential parsing ([`specs/constitution.md:10`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/specs/constitution.md#L10)). `IssueRecord` is a Pydantic model with a constrained status — `DRAFT`, `BACKLOG`, `SPECIFIED`, `SHARDED`, `COMPLETED` — in [`src/deviate/state/ledger.py:26-38`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/state/ledger.py#L26-L38).

A transition is an appended row, not an edit in place. `append_issue_transition` uses the `(issue_id, status)` pair as an idempotency key, so `BACKLOG → SPECIFIED → SHARDED → COMPLETED` can remain observable without duplicating the same transition ([`src/deviate/state/ledger.py:146-157`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/state/ledger.py#L146-L157)). `resolve_issue_record` reads those rows and gives terminal `COMPLETED` precedence, while the latest valid non-terminal row remains the fallback ([`src/deviate/state/ledger.py:183-239`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/state/ledger.py#L183-L239)).

Git then gets a deliberately boring merge rule:

```gitattributes
specs/issues.jsonl merge=union
specs/**/tasks.jsonl merge=union
```

Those are the exact attributes in [`.gitattributes:1-5`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/.gitattributes#L1-L5). Concurrent appends are unioned instead of made into a line-level merge fight. The merge command closes the loop: `_merge_run` copies the resolved `IssueRecord`, changes only `status` and `timestamp`, and calls `append_issue_transition` to write `COMPLETED` ([`src/deviate/cli/meso.py:1818-1866`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/cli/meso.py#L1818-L1866)). The public `merge` command is the wrapper for that operation ([`src/deviate/cli/meso.py:1953-1984`](https://github.com/wernerbisschoff/deviatdd/blob/a8b1e4a/src/deviate/cli/meso.py#L1953-L1984)).

## Why append-only, not mutable state

The wrong path is a single mutable `status` field that gets overwritten by whichever worktree pushes last. That path loses the claim, the hand-off, and the evidence that a gate happened. It also turns concurrency into a race disguised as a successful write.

Append-only changes the question. Instead of “what is the current value?” the system asks “what sequence of transitions produced this value?” A branch claim is an event. A plan completion is an event. A merge is an event. Resolution is a deterministic fold over events, with `COMPLETED` treated as terminal. Git stores the history; JSONL keeps the history inspectable; union merge keeps independent appends composable.

This is not event-sourcing theatre. It buys three concrete properties: **auditability** (the old rows stay), **idempotence** (repeating a transition is safe), and **re-derivability** (a damaged working copy can be rebuilt from the ledger). The cost is that readers must understand the fold. That is a better cost than asking a future agent to infer a vanished state from a branch name.

## What I'd push back on

First, `merge=union` is a conflict policy, not a semantic merge. It avoids textual conflicts, but it cannot decide whether two rows are duplicate claims, whether two competing `SPECIFIED` transitions describe the same work, or whether a late append is causally valid. `resolve_issue_record` protects the terminal `COMPLETED` case; it does not make every cross-branch sequence meaningful. Union is a good default for append-only files, not a proof that concurrent work is coherent.

Second, monorepo scale will stress the path shape. A single `specs/issues.jsonl` and a shared `feat/<epic>/<issue>` namespace are legible while the issue set is small. With many teams, epics, and long-running worktrees, the ledger becomes a hot file and branch discovery becomes a coordination surface. Sharding ledgers by product or epic could reduce contention, but then resolution, union rules, and cross-shard references need a contract of their own. I would not add that complexity until measurements show the shared ledger is the bottleneck.

## What I still don't know

I don't know how a claim ages. A long-lived branch can remain a truthful ownership record while its Product assumptions, Macro PRD, or Meso plan change underneath it. The branch name still points to the issue, but the original contract may no longer be the contract being implemented. What is the right expiry or re-approval rule for a claim that survives several release cycles?

I also don't know the re-derivation cost at scale. Replaying one JSONL ledger is straightforward; replaying years of issue, task, and flow events across a monorepo may be slower and harder to explain than reading a snapshot. The framework currently chooses history over snapshots. I want a measured answer for when a materialized view becomes necessary — without turning that view into the mutable source of truth the append-only protocol was meant to avoid.

The open-source implementation is at [github.com/wernerbisschoff/deviatdd](https://github.com/wernerbisschoff/deviatdd). The next useful test is not another prompt tweak; it is a concurrent claim, a delayed merge, and a replay of the resulting ledgers.
