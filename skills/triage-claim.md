# Skill — Triage Claim

## Purpose

Take a raw FNOL (phone transcript, form submission, or handler dictation) and produce a structured triage brief the handler can act on in under 30 seconds.

## Input

A free-text description of a claim, often messy, sometimes incomplete. May or may not include a policy number.

## Output

```
CLAIM TYPE
(motor / home / travel — and sub-type, e.g., motor / storm damage)

SEVERITY
(low / medium / high — with one-line reason)

POLICY SECTIONS LIKELY RELEVANT
(list specific clauses, e.g., "Motor §4.2 Storm damage", "Motor §8 Excess")

FACTS WE HAVE
(bullet list, labelled clearly)

MISSING INFO THE HANDLER SHOULD COLLECT
(bullet list)

RED FLAGS
(fraud signals, vulnerability signals, complexity signals — or "none identified")

SUGGESTED NEXT ACTION
(one line)
```

## Severity rubric

- **High** — injury, fatality, large loss, potential total loss, unoccupied home, third-party property damage with complexity, any regulatory/media angle.
- **Medium** — standard motor accidental damage, contained home escape-of-water, theft with police report, travel cancellation.
- **Low** — windscreen-only, single-item travel baggage, minor cosmetic damage.

## Fraud signal checklist

Flag any of the following, but never communicate suspicion to the customer:

- Loss occurs shortly after policy inception or recent increase in cover.
- Inconsistent dates or times across the customer's account.
- Customer declines to provide a police report for theft.
- Photographs suggest damage older than claimed date.
- Vague or shifting description of how the loss occurred.
- Previous similar claims.
- Customer pushes unusually hard for a quick settlement.

## Vulnerability signal checklist

- Bereavement mentioned.
- Signs of confusion or memory difficulty in the account.
- Language barrier.
- Caller mentions financial distress ("I need this money fast or I'll…").
- Caller is visibly emotional to a degree that impairs information exchange.

## Worked example

See `examples/triage-example.md`.
