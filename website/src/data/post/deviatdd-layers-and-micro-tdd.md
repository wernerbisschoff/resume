---
title: 'DeviaTDD: A Spec-First Agent Orchestration Framework'
publishDate: 2026-07-01T00:00:00Z
draft: true
excerpt: 'Most AI coding agents stop at generation — code compiles, tests go green, the diff lands. DeviaTDD is a spec-first, agent-agnostic framework that runs the entire TDD cycle with three non-bypassable human gates and a conditional test-amendment phase (Yellow) that is the load-bearing piece.'
category: DeviaTDD
tags:
  - deviatdd
  - release
author: Werner Bisschoff
---

Most AI coding agents stop at generation. The code compiles, the tests go green, the diff lands. Verification is treated as a post-hoc audit, not a structural property of the loop.

**DeviaTDD is a spec-first, agent-agnostic framework that runs the entire TDD cycle — explore, spec, red, green, refactor — with three non-bypassable human gates and a conditional test-amendment phase (Yellow) that distinguishes agent cheating from a genuine spec error.**

The framework is MIT-licensed, written in Python, and ships as a single CLI. The first-commit install is `uv tool install deviate`; the first slash command is `/deviate-explore "..."`. Claude Code, OpenCode, Pi, and Droid are first-class backends.

## The problem: tests pass, code is wrong

The pattern in the agentic engineering literature is consistent. Frontier models ship plausible-looking code that fails in three documented ways:

- **Generation-only agents hack the test** to make a failing check pass. METR 2025 evaluations document models modifying test/scoring code; the Anthropic model card describes `sys.exit(0)` to make all tests appear to pass. TDFlow caught 7 test-hacking instances across 800 SWE-Bench runs — every one counted as a failure.
- **Long chats lose the customer mental model.** The agent's idea of "what we're building" drifts toward whatever the latest spec says, which is rarely what the user asked for.
- **Parallel features contradict each other.** Two correct features can produce a broken system. Without a place where cross-feature coherence is reviewed, no review catches it.

The general-purpose mitigation is "be more careful." DeviaTDD's mitigation is structural: each phase is a non-bypassable artifact transition, and each transition is gated on a check the agent cannot fake.

## The framework: four layers, three gates, one micro-loop

DeviaTDD decomposes a feature into a chain of artifacts. Each artifact is a separate commit. The chain is not a checklist; it is a routing problem — each phase uses a different model tier and produces a distinct form of evidence.

### The four layers

**Product _(optional)_ — customer framing.** Three artifacts: _flows_ (actor, job, trigger), _architecture_ (cross-product data and components), and _release_ (a single-sentence contract with users). Most repos ship one feature stream at a time and skip this layer; multi-product repos do not. The layer exists to keep the agent's mental model of "the product" anchored to a customer, not to the latest spec.

**Macro — feature scoping.** Four phases: _explore_ (a factual "what exists" scan, no recommendations), _research_ (architectural reasoning, **Gate 1** review), _prd_ (testable acceptance criteria in EARS notation), and _shard_ (vertical-slice issue files, **Gate 2** review). A complexity-classified _adhoc_ shortcut condenses the four into one issue for low/medium-complexity work; the gate rejects it for high-complexity work.

**Meso — issue engineering.** Two phases: _plan_ (per-issue localized research that reads prior issues from the issues ledger) and _tasks_ (4–8 TDD-executable tasks with explicit DAG `blocked_by` dependencies). `tasks.md` is the human's review surface; `tasks.jsonl` is the CLI's execution surface. They are separate files because the formats serve different readers.

**Micro — per-task loop.** The default is the TDD micro-cycle described below. Low-complexity tasks route to `/deviate-execute` and skip the cycle but keep their own Judge pass.

### The three non-bypassable human gates

| Gate                  | What is reviewed                                        | Failure mode it catches                                                          |
| --------------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Gate 1 — design**   | `design.md` + `data-model.md` after `/deviate-research` | Bad architecture decisions that propagate through every issue                    |
| **Gate 2 — contract** | Every sharded issue file before meso planning           | Spec errors that cascade through every TDD cycle                                 |
| **Gate 3 — merge**    | Final PR scan before merge                              | Integration regressions, doc drift, scope creep that escaped per-task validation |

Gates are cheap. A five-minute human check at Gate 1 prevents a multi-day agent cycle that built the wrong thing. One gate at the end is too late; a gate at every micro-step is bureaucracy. Three gates correspond to the three failure modes that compound across the lifecycle: bad design, bad contract, bad merge.

### Why the four layers, not one big prompt

A single prompt that does exploration, spec writing, decomposition, and TDD is a single context window that has to hold all four roles at once. The model loses the discipline of one role while playing another. Splitting the work into layers — each a small artifact, a separate commit, a separate review — converts a long chat into a chain of reviewed briefs.

The strongest evidence for this comes from TDAD, which measured a 70% regression reduction from pre-computed `test_map.txt` + ≤30-line `SKILL.md`, and from SCOPE-V: _do not let an agent implement from a long chat; let it implement from a reviewed brief_. TDAD's finding that shrinking `SKILL.md` from 107 to 20 lines quadrupled resolution (12% → 50%) is the empirical case for the layer's design philosophy: the right-sized, well-bounded, reviewable artifact beats the comprehensive-but-soft prompt.

## The TDD micro-loop: `Red → Green → [Yellow] → Judge/Train → Refactor`

The micro-loop is the part the rest of the framework rests on. It is also the part that deviates most from the textbook TDD cycle.

**Red — write a failing test first.** A test written after implementation reflects what the code does, not what it should do; this is _context pollution_, documented in TDAD and TDAID. A test that passes immediately is not a test — it is an assertion that whatever the implementation does is correct, which is exactly the rationalisation the loop exists to prevent. Red writes a failing test in a session with no production code. The test is the agent's only objective specification.

**Green — minimum code to pass.** Documented frontier-model failures include deleting scoring code and calling `sys.exit(0)` to make tests appear to pass. "Do not change the tests" is not an instruction DeviaTDD trusts the agent with; it is _structural enforcement_ the agent cannot bypass. The **Tamper Guard** reverts any test edit made during green before the suite runs. The implementation is bounded by the test, not by the agent's idea of "right."

**Yellow _(conditional)_ — the test-amendment gate.** This phase fires only when green edited the test. Both "agent cheating" and "agent caught a real spec error" look identical in the diff — the test file changed. Silently reverting the test forces the loop to fail on a test the agent correctly identified as broken; silently accepting allows test-hacking to slip through. Yellow is the only structurally safe path between the two: the agent's proposed amendment is routed to a human for review, and the human decides which case it is. The phase is the load-bearing piece of the micro-loop.

Yellow is also the only phase in the framework with no direct literature source — it is a DeviaTDD-original pattern. The general principle ("agents cannot self-verify") is well-cited (IACDM, PRIME), but the specific "test-amendment gate" pattern is not. The pattern is the single most consequential evidence gap in the framework, and the part most worth press-testing.

**Judge/Train — independent review with bounded repair.** The same agent that wrote the green code cannot reliably review it. Judge runs in an isolated session with a fresh context, evaluates the production diff against the contract, and returns `JUDGE_PASS` or `JUDGE_REJECTED`. On rejection, the CLI rolls back to the RED commit, injects the failure feedback into the next green prompt, and retries — up to three times. The bound forces escalation back to the human. The feedback is the only signal the next attempt gets for what the compliance checker objected to. Three retries is enough; more is a sign of a wrong test or a wrong spec, not a wrong model.

**Refactor — behavior-preserving improvement.** Refactor's benefits are delayed and invisible; without an explicit phase, it gets skipped. Refactor runs only on `JUDGE_PASS`, with the green test suite as its safety net. If the refactor breaks a test, the CLI discards it and the task completes on the verified GREEN. The discipline of "tests must still pass when you're done" is the refactor's definition. If a refactor requires changing a test, the original code was wrong, not just ugly — that is a Judge issue, not a refactor issue.

## What you can do with it

Install the CLI:

```bash
uv tool install deviate
deviate setup --agent claude     # or: opencode | pi | droid
```

Bootstrap creates `.deviate/`, scaffolds `specs/constitution.md`, and installs `/deviate-*` slash commands for every supported backend. The first feature is then a chain of slash commands — `/deviate-explore`, `/deviate-research`, `/deviate-prd`, `/deviate-shard`, `/deviate-plan`, `/deviate-tasks`, `/deviate-red`, `/deviate-green`, `/deviate-judge`, `/deviate-refactor`, `/deviate-pr`, `/deviate-review` — each producing one committed artifact, each gated where the framework says a gate belongs.

The full lifecycle takes a problem statement to merged, tested code with a documented audit trail. The trail is append-only JSONL (`specs/<epic>/issues/ISS-NNN/tasks.jsonl`, `specs/issues.jsonl`), and a corrupted state file can be reconstructed by re-running the event stream.

The framework is open source under MIT. Issues, PRs, and adversarial examples of test-hacking are welcome at [github.com/wbisschoff13/deviatdd](https://github.com/wbisschoff13/deviatdd). The Yellow phase is a single slash command: `/deviate-yellow <task-id>`. If you have an agent loop, the question is whether your framework can distinguish a correct test critique from a cheated test. If it cannot, the Tamper Guard is a vulnerability.
