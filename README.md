# Claims Copilot

> A context folder for an insurance claims handler, not a prompt.

This repo is an opinionated example of **context engineering** for a regulated, high-stakes role. It shows how I'd set up an AI assistant for a first-notice-of-loss (FNOL) claims handler — the person on the other end of the phone when your car gets hit or your house floods.

The philosophy: a good assistant isn't one clever prompt. It's a role definition, a knowledge base, a set of skills, guardrails that reflect real regulation, worked examples, and evals that tell you when it's drifting.

All policy wordings, claim files, and customer data in this repo are **synthetic**. Nothing here is real content.

---

## What's in here

```
claims-copilot/
├── AGENT.md               # The role, guardrails, and reasoning pattern
├── knowledge/             # What the agent knows
│   ├── policy-wordings/   # 3 synthetic policies (motor, home, travel)
│   ├── regulatory.md      # GDPR + fair-treatment rules the agent must follow
│   ├── style-guide.md     # Tone of voice, empathy, forbidden phrases
│   └── glossary.md        # Claims jargon, demystified
├── skills/                # What the agent can do (sub-playbooks)
│   ├── triage-claim.md
│   ├── coverage-check.md
│   ├── draft-letter.md
│   └── summarize-file.md
├── examples/              # Worked input→output pairs per skill
├── evals/                 # How we know it works
│   ├── cases.json
│   └── run.py
└── demo/
    └── app.py             # Streamlit demo
```

---

## Tutorial: how to use it

### Option A — Drop it into Claude (fastest)

1. Open a new Claude Project (or conversation).
2. Copy the contents of `AGENT.md` into the Project system prompt / custom instructions.
3. Upload the `knowledge/` folder contents as project files.
4. Start chatting. Try:
   > "New FNOL just came in. Customer says a tree fell on their car overnight during the storm. Policy number MOT-2024-0192. Triage it."

### Option B — Run the demo app

```bash
pip install streamlit anthropic
export ANTHROPIC_API_KEY=sk-ant-...
streamlit run demo/app.py
```

The app lets you paste in an FNOL and pick a skill (triage, coverage check, draft letter, summarize). It loads `AGENT.md` + the relevant skill file + knowledge as context and returns a structured response.

### Option C — Run the evals

```bash
pip install anthropic
python evals/run.py
```

This runs 18 test cases through the agent and scores responses with Claude-as-judge on four dimensions: factual accuracy, guardrail adherence, tone, and usefulness. Outputs a JSON report.

---

## Why it's built this way

**AGENT.md over a giant prompt.** One file, version-controlled, reviewable by a compliance officer. No one should have to scroll a 4,000-token wall of text to understand what the agent does.

**Skills as separate files.** A claims handler doesn't do one thing. Triage, coverage analysis, and letter-drafting each have different inputs, outputs, and risks. Separating them lets us iterate on one without breaking the others.

**Guardrails are specific, not generic.** "Be helpful and harmless" doesn't survive contact with a customer who just totaled their car. The AGENT.md has explicit "never do" rules grounded in real regulatory concerns (setting reserves, admitting liability, quoting settlement figures).

**Evals are the point.** Anyone can write a prompt. Knowing whether it works on the 18th edge case is what separates a demo from a system.

---


Built as a portfolio piece. Feedback very welcome.
