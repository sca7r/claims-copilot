# Skill — Draft Letter

## Purpose

Produce a customer-facing letter or email the handler can edit and send. Three templates are supported:

1. **Acknowledgement** — we've received your claim, here's what happens next.
2. **Information request** — we need X to progress.
3. **Decision** — your claim is being settled / partially settled / declined.

## Input

- The claim facts.
- Which template.
- For decisions: the outcome and the reason, with clause references.
- Any known vulnerability flags (adjusts tone).

## Output

A complete draft letter following `knowledge/style-guide.md`, ready for handler review. Include a subject line. Do not include a signature block — the handler adds theirs.

## Hard rules

- Start with acknowledgement, not with logistics.
- For decline letters: state the outcome clearly in the first or second paragraph. Don't bury.
- For decline letters: always include the customer's right to complain and a realistic path to appeal.
- Never state a settlement figure unless explicitly given by the handler.
- Never use "we regret to inform you" or "please be advised."
- If the claim involves bereavement or other vulnerability, soften the opening further and add no time pressure.

## Template skeletons

### Acknowledgement

```
Subject: We've received your claim — reference [REF]

Dear [Name],

We're sorry to hear about [what happened]. We've received your claim and I'm
looking after it from here.

Here's what happens next:
1. [specific next step with owner and timeframe]
2. [...]

If you have any questions, you can reach me on [contact] between [hours].

Thank you for your patience while we work through this.
```

### Information request

```
Subject: Quick update on your claim [REF] — we need a bit more from you

Dear [Name],

Thanks for letting us know about [incident]. To move your claim forward, we need:

- [specific item, with a one-line explanation of why]
- [...]

The easiest way to send these is [method]. No rush — but as soon as we have
them, we can [what happens next].
```

### Decision (decline)

```
Subject: Outcome of your claim [REF]

Dear [Name],

We're sorry to hear about [incident], and we understand this will not be
the news you were hoping for.

After reviewing your policy and the circumstances, we're unfortunately not
able to settle this claim. The reason is [plain-language version of the
clause], which is set out in [clause reference] of your policy wording.

[One short paragraph explaining what that means in practice, without jargon.]

If you disagree with this outcome, you have the right to ask us to review it.
You can do this by [complaints process]. You also have the right to refer
your complaint to [ombudsman] if you remain unhappy with our final response.

[Contact details]
```

## Worked example

See `examples/letter-example.md`.
