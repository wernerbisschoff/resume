---
title: "Why DeviaTDD's micro-loop is Red → Green → Judge/Train → Refactor"

publishDate: 2026-07-09T00:00:00Z
draft: false
excerpt: 'The micro-loop is four phases — Red, Green, Judge/Train, Refactor — each exists because the model has a documented failure mode the phase prevents. Judge verifies the implementation; Train rolls back to red_sha, injects the rejection feedback, and re-runs Green. Verification is structurally separate from generation, enforced by git itself.'
category: DeviaTDD
tags:
  - deviatdd
  - tdd
  - agent-orchestration
  - state-machines
author: Werner Bisschoff
metadata:
  description: 'The micro-loop is four phases — Red, Green, Judge/Train, Refactor — each exists because the model has a documented failure mode the phase prevents. Judge verifies the implementation; Train rolls back to red_sha, injects the rejection feedback, and re-runs Green. Verification is structurally separate from generation, enforced by git itself.'
---

I'm a solo neurodivergent SWE on South African infrastructure. Every commit has to be recoverable from git alone — no cloud state to reconstruct, no Slack thread to dig through. The micro layer is the smallest unit DeviaTDD's loop can break into, and the only one where the artifact is executable code. Above the micro layer, the artifacts are specs, plans, and tasks — not tests. Spec-driven development applies there. TDD applies here.

The micro cycle is `Red → Green → Judge/Train → Refactor`. The phase constants are declared at `src/deviate/cli/micro.py:130-133`:

```python
_SKILL_NAMES: dict[str, str | None] = {
    "RED": "deviate-red",
    "GREEN": "deviate-green",
    "JUDGE": "deviate-judge",
    "REFACTOR": "deviate-refactor",
    "EXECUTE": "deviate-execute",
}
```

Four phases, no conditional branches in the cycle body. Each phase exists because the model has a documented failure mode the phase prevents.

## The four phases

**Red — write a failing test first.** A test that passes immediately is not a test — it reflects what the code does, not what it should do. Per [TDD Governance](https://arxiv.org/abs/2604.26615)'s phase-ordering rule, no production code is permitted until a failing-test state exists. [TDAID](https://www.awesome-testing.com/2025/10/test-driven-ai-development-tdaid) frames this as the difference between "tests as validation" (after the fact) and "tests as spec" (before). Red writes a failing test in a session with no production code. The test is the agent's only objective specification.

**Green — minimum code to pass.** Bounded by the test, not the prompt. Documented frontier-model failures include deleting scoring code and calling `sys.exit(0)` to make the run appear to succeed — [TDFlow's evaluation pipeline](https://arxiv.org/abs/2510.23761) caught the pattern 7 times across 800 SWE-Bench runs (300 Lite + 500 Verified), all counted as failures. [Agent Patterns: Red-Green-Refactor for Agents](https://agentpatterns.ai/verification/red-green-refactor-agents/) puts it well: the red test is the agent's goal; the implementation is just a means to that goal. Minimum-code-to-pass is the only code that is verifiably correct — anything beyond is unverified.

**Judge — independent verification of the diff against the spec.** The same model that wrote the green code cannot reliably review it. Judge runs in an isolated session with a fresh context, evaluates the production diff against the contract, and returns `JUDGE_PASS` or `JUDGE_REJECTED`. If the verifier rejects — out-of-scope edits, missing edge cases, intent that doesn't match the test — Judge hands off to Train. Verification without a repair path is a dead end.

**Train — the repair half of the same phase.** On rejection, the framework executes `git reset --hard red_sha` at `micro.py:1192` and injects the rejection feedback into the next Green attempt's prompt at `micro.py:980-981`:

```python
if session.train_feedback:
    prompt += f"\n\n<train_feedback>\n{session.train_feedback}\n</train_feedback>\n"
```

Green re-runs against the same red commit. The retry cap is enforced at `micro.py:1682-1683` (`train_attempts = 0; max_train_attempts = 3`) and re-armed on `JUDGE_REJECTED` at line 1743, with the [bounded-repair budget](https://arxiv.org/abs/2604.26615) TDD Governance specifies.

Why this is structural, not a longer prompt: the [IACDM verification gap thesis](https://arxiv.org/abs/2604.16399) and [PRIME's Executor/Verifier asymmetry](https://doi.org/10.20944/preprints202601.1479.v1) are explicit on this — the same model that produced a design will produce a plausible-looking review of it. Adding more context to the same model does not close a structural gap; it widens it. [State Contamination's SPG analysis](https://arxiv.org/abs/2605.16746) is the empirical version of the same point: sub-threshold propagation gap (SPG) is the difference between what thresholded monitoring flags and what behaviorally activates — on the order of SPG(τ=0.5) ≈ 0.14 (p < 10⁻⁷ per the State Contamination paper), with sub-threshold effects at every monitored threshold. Self-verification is not neutral.

**Refactor — behavior-preserving cleanup.** Only runs after Judge passes. The green suite is the refactor's safety net; any behavior change breaks a test, which Judge catches and rolls back. Per Agent Patterns: refactor is safe only while the test suite passes — after Judge, the test suite is the refactor's safety net. Refactor must be behavior-preserving — never test-preserving. If a refactor requires changing a test, the original code was wrong, not just ugly.

## Why I dropped Yellow

The first version of the micro cycle had a conditional fifth phase: Yellow, a test-amendment gate. When Green modified a test file, a TamperGuard detected the change, the agent proposed an amendment in an isolated session, and a human judge decided whether the amendment was a real spec error or cheating. I removed it in v2.2.0 — 30 files changed, 1,888 deletions, commit [`0adcc83`](https://github.com/wernerbisschoff/deviatdd/commit/0adcc831eb676f2ba24f7d364989f07587b57945).

The wrong path was treating verification as a prompt problem. The first instinct when an agent produces a bad review of its own code is to add instructions — "be more rigorous", "check your work", "consider edge cases". Yellow was a more elaborate version of that instinct: a separate phase, a separate prompt, a separate agent — but still a longer prompt, not a different process. The TamperGuard fired rarely, and when it did, the conditional branch cost more to prompt and debug than Judge's straight-line scope check saved. Judge already enforces that Green may only write to `src/` and permitted paths; modifications to `tests/`, `specs/`, or config files are flagged as scope violations directly. The same constraint, in a straight line, is simpler to prompt, simpler to debug, and cheaper to run.

Every conditional branch in a state machine my agents execute is a cognitive tax. Agents don't reason about state machines the way I do — they follow the prompt's flow description. A conditional branch means the prompt must describe two paths, the agent must evaluate which path applies, and the orchestration must handle both outcomes. Four phases, no conditional branches: the cycle is `Red → Green → Judge/Train → Refactor`, and every state transition is git-visible; every rejection is auditable; every rollback is to a known-good commit, not a fresh start.

## What I'd push back on

The bounded-repair cap of N=3 was empirically validated on the model tiers I run locally. [TDD Governance](https://arxiv.org/abs/2604.26615) frames N=3 as the empirical cap — "may be insufficient for models with low instruction-following capability" — so the cap is a starting point, not a constant. [TDDev's](https://arxiv.org/abs/2605.17242) protocol-model fit found a 25× cost penalty for mismatch — a cheap conservative model on a high-enforcement protocol versus a holistic model on a low-enforcement protocol. The N=3 that holds on Sonnet may be insufficient on Qwen 3.7 and over-bounded on a frontier-tier reasoning model. The cap needs to be per-model-tier, not a global constant.

The other thing I'd push back on is the assumption that Judge running on a different model tier is sufficient. `specs/constitution.md` §1 hedges this: the `claude` backend silently ignores the `.deviate/config.toml` `[models]` section (`specs/constitution.md:16`), so in practice the model separation only works with `opencode` or `droid` backends. The structural separation principle survives — git still rolls back, the `red_sha` still anchors the retry — but the asymmetric-verifier principle weakens when Green and Judge share a model tier on a non-routing backend. This is a configuration tax, not a framework tax.

## What I still don't know

I don't know how N=3 holds across very long horizons — runs of 24+ task loops in a single sprint, with each loop producing a fresh judge verdict. The bounded-repair pattern assumes the retry distribution is roughly stationary across the loop. If late-loop retries start failing in correlated ways (because the underlying spec drifted across loops, not because the implementation is wrong), N=3 misfires: the rollback preserves the red commit but the loop terminates without surfacing the spec drift. The Meso layer's Gate 2 (contract sign-off) should catch this, but I haven't tested whether it does in practice.

I also don't know how this holds up under adversarial specs — specs designed to look correct but contain subtle contradictions. The bounded-repair loop's N=3 retries would all fail, and the rollback would correctly preserve the red commit, but the loop terminates without surfacing the spec contradiction to the human reviewer at the right layer. Spec hygiene is upstream of micro-loop reliability, and I don't have an automated mechanism for it yet.

The framework is open source under MIT and lives at [github.com/wernerbisschoff/deviatdd](https://github.com/wernerbisschoff/deviatdd). Issues, PRs, and adversarial examples of test-hacking are welcome.

## References

1. ["TDD Governance for Multi-Agent Code Generation via Prompt Engineering"](https://arxiv.org/abs/2604.26615) — N=3 bounded-repair cap framing.
2. ["Interactive Adversarial Convergence Development Methodology (IACDM)"](https://arxiv.org/abs/2604.16399) — verification-gap thesis.
3. ["PRIME: Policy-Reinforced Iterative Multi-Agent Execution for Algorithmic Reasoning in Large Language Models"](https://doi.org/10.20944/preprints202601.1479.v1) — Executor/Verifier asymmetry.
4. ["State Contamination in Memory-Augmented LLM Agents"](https://arxiv.org/abs/2605.16746) — sub-threshold propagation gap (SPG) analysis: SPG(τ=0.5) ≈ 0.14 (p < 10⁻⁷).
5. ["From Runnable to Shippable: Multi-Agent Test-Driven Development for Generating Full-Stack Web Applications from Requirements"](https://arxiv.org/abs/2605.17242) — TDDev's protocol-model fit; 25× cost penalty for mismatch.
6. ["TDFlow: Agentic Workflows for Test-Driven Development"](https://arxiv.org/abs/2510.23761) — 7 test-hacking instances detected across 800 SWE-Bench runs.
7. ["Test-Driven AI Development (TDAID)"](https://www.awesome-testing.com/2025/10/test-driven-ai-development-tdaid) — "tests as spec" vs "tests as validation" framing.
8. [Agent Patterns: Red-Green-Refactor for Agents](https://agentpatterns.ai/verification/red-green-refactor-agents/) — test-state as externally observable stopping criterion.
