---
title: 'When the Safety Net Becomes the Complexity'
publishDate: 2026-07-02T00:00:00Z
draft: false
excerpt: "The YELLOW test-amendment gate and TamperGuard added a conditional branch to the DeviaTDD micro-layer that didn't earn its complexity — so we removed it."
category: DeviaTDD
tags:
  - deviatdd
  - tdd
  - agent-orchestration
  - state-machines
author: Werner Bisschoff
metadata:
  description: "The YELLOW test-amendment gate and TamperGuard added a conditional branch to the DeviaTDD micro-layer that didn't earn its complexity — so we removed it."
---

## What we removed

Thirty files changed, 1,888 deletions, one conditional branch removed: the DeviaTDD (test-driven development for LLM agents) micro-layer no longer has a YELLOW phase. YELLOW was a test-amendment gate — when GREEN (the implementation phase) modified test files, TamperGuard detected the change and triggered a separate YELLOW phase where the agent proposed test changes, an isolated Yellow Judge evaluated them against `spec.md`, and the cycle continued or reverted. It ran on V4 Pro (the premium compliance model tier) in an isolated session with no context cache sharing. It fired rarely.

The intent was sound: prevent agents from weakening tests to pass. The execution added a conditional branch to a state machine that agents already struggled to navigate.

I'm a neurodivergent SWE working from Cape Town on South African budgets — every extra conditional branch is one more thing my brain and my cloud bill have to track. That's the real cost of YELLOW: not just the V4 Pro session, but the cognitive tax of maintaining a branch in a state machine I have to hold in my head.

## What YELLOW actually added

The micro-layer cycle was RED → GREEN → [TamperGuard → YELLOW?] → JUDGE → REFACTOR. YELLOW was not a fixed phase in the phase map — it was a conditional branch in the cycle body between GREEN and JUDGE. When triggered, it meant:

- A proposal schema (`yellow_trigger`, `test_changes`, `rationale`) embedded in the GREEN handover manifest.
- An isolated V4 Pro session for the Yellow Judge (no cache sharing with the preceding GREEN turn — a 2× cost multiplier).
- Two CLI commands (`yellow_pre`/`yellow_post`) with approve/reject verdicts.
- Three status literals in `TaskRecord` (`YELLOW`, `YELLOW_APPROVED`, `YELLOW_REJECTED`).
- A `yellow_triggered` field on `SessionState` and a `yellow_trigger` field on `HandoverManifest`.

All of this to handle a case that JUDGE already covered: GREEN may only write to `src/` and permitted paths; modifications to `tests/`, `specs/`, or config files are flagged as scope violations by JUDGE directly.

## Why we removed it

I was anxious about removing a safety gate. YELLOW was supposed to be the thing that kept agents honest — the phase that caught them weakening tests to pass. Dropping it felt like removing a lock from a door. But the numbers forced the change: TamperGuard fired rarely, and when it did, the conditional branch cost more to prompt and debug than JUDGE's straight-line scope check saved.

The wrong path was assuming that a conditional branch in the cycle body was cheaper than a scope check at the phase boundary. It wasn't. The branch added indirection that was harder for agents to follow than a simple validation at the end.

Removing YELLOW eliminated the `TamperGuard`/`TamperContext`/`TamperVerdict` classes, the `yellow_pre`/`yellow_post` CLI commands, the `deviate-yellow` skill prompt, and all YELLOW orchestration from the TDD cycle. The cycle is now RED → GREEN → JUDGE → REFACTOR — four phases, no conditional branches.

The same commit also fixed a latent race condition in the research pipeline: Gamma (adversarial audit) was instructed to read Alpha and Beta outputs that ran in parallel with it. Merging Alpha/Beta into a single sequential AlphaBeta stage and running Gamma strictly after eliminated the race.

**30 files changed. 1,888 deletions.** Version bumped to 2.2.0. See commit [0adcc83](https://github.com/wernerbisschoff/deviatdd/commit/0adcc831eb676f2ba24f7d364989f07587b57945).

## What I'd do differently

The original YELLOW design assumed TamperGuard's conditional branching was cheaper than JUDGE's scope checking. It wasn't. The conditional branch added indirection that was harder for agents to follow than a simple scope check.

In state machines that LLM agents execute, every conditional branch is a cognitive tax. Agents don't reason about state machines the way human developers do — they follow the prompt's flow description. A conditional branch means the prompt must describe two paths, the agent must evaluate which path applies, and the orchestration must handle both outcomes. A straight-line cycle with scope checks at the end is simpler to prompt, simpler to debug, and cheaper to run.

I'd build the next iteration of any agent-executed state machine with zero conditional branches in the cycle body. Scope checks belong at phase boundaries, not as intermediate gates.

I don't know yet how far I can push "no conditional branches" before safety genuinely does need a mid-cycle gate. JUDGE catches scope violations, but it doesn't catch _weakened test assertions_ — the case where GREEN modifies a test to make it pass without actually fixing the bug. That's the gap YELLOW was built to fill, and right now it's open.
