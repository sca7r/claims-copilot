# Skill — Coverage Check

## Purpose

Given a set of facts and a policy wording, give the handler a preliminary coverage view. This is a view, not a decision.

## Input

1. The facts of the claim (from the FNOL or triage output).
2. The relevant policy wording (full or extract).
3. Optionally, the policy schedule (for excess, extensions, limits).

## Output

```
PRELIMINARY VIEW
(covered / likely covered / likely not covered / insufficient info — with a one-line reason)

CLAUSE-BY-CLAUSE REASONING
- Clause reference and text summary
- How the facts map to it
- Any ambiguity

FACTS THAT WOULD CHANGE THE VIEW
(bullet list of "if we learn X, the view shifts to Y")

EXCESS / LIMITS IMPACT
(what the customer will likely pay or receive, if the claim proceeds)

HANDLER DECISION POINTS
(what the handler needs to decide or investigate to finalize)
```

## Hard rules

- The word "covered" in the preliminary view is always qualified ("likely", "preliminary").
- Never tell the customer any of this. Coverage decisions are communicated by the handler after their own review.
- If the wording isn't in the context, refuse to answer and ask for it. Do not reason from general knowledge of what "motor policies usually say."
- Cite every clause you rely on by its reference, not just its content.

## Common patterns

- **Storm damage to car:** check §4.2 wind-speed threshold, check §4.3 gradual-deterioration exclusion, check general exclusions in §7.
- **Escape of water (home):** §4.3, specifically the "gradual leak" carve-out. Age of plumbing matters.
- **Travel cancellation:** §3, and specifically whether the reason falls inside the named-reasons list or into the "disinclination to travel" exclusion.

## Worked example

See `examples/coverage-check-example.md`.
