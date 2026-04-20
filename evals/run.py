"""
Eval runner for Claims Copilot.

For each case in cases.json, it:
  1. Builds the context (AGENT.md + relevant skill + knowledge).
  2. Calls Claude with the case input.
  3. Scores the response with Claude-as-judge against the case's expectations.
  4. Writes a JSON report.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python evals/run.py
"""

import json
import os
import sys
from pathlib import Path

try:
    from anthropic import Anthropic
except ImportError:
    print("Install: pip install anthropic")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
MODEL = "claude-opus-4-7"
JUDGE_MODEL = "claude-opus-4-7"

client = Anthropic()


def load_context(skill: str) -> str:
    """Load AGENT.md + skill playbook + all knowledge files as a single system prompt."""
    parts = []
    parts.append("# AGENT\n\n" + (ROOT / "AGENT.md").read_text())

    skill_map = {
        "triage": "triage-claim.md",
        "coverage": "coverage-check.md",
        "letter": "draft-letter.md",
        "summary": "summarize-file.md",
    }
    if skill in skill_map:
        parts.append(
            "# ACTIVE SKILL\n\n" + (ROOT / "skills" / skill_map[skill]).read_text()
        )

    knowledge_dir = ROOT / "knowledge"
    for p in sorted(knowledge_dir.rglob("*.md")):
        rel = p.relative_to(ROOT)
        parts.append(f"# KNOWLEDGE — {rel}\n\n" + p.read_text())

    return "\n\n---\n\n".join(parts)


def run_agent(case: dict) -> str:
    system = load_context(case["skill"])
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": case["input"]}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


JUDGE_PROMPT = """You are evaluating a response from an AI claims assistant against a list of expectations.

For each expectation, output PASS or FAIL with a one-line reason.

Then give:
- overall_score: 0–10
- summary: one sentence
- most_important_issue: one sentence (or "none")

Respond ONLY in JSON:
{
  "per_expectation": [{"expectation": "...", "verdict": "PASS|FAIL", "reason": "..."}],
  "overall_score": 0,
  "summary": "...",
  "most_important_issue": "..."
}
"""


def judge(case: dict, response: str) -> dict:
    user_msg = f"""CASE INPUT:
{case['input']}

EXPECTATIONS:
{json.dumps(case['expectations'], indent=2)}

AGENT RESPONSE:
{response}
"""
    resp = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=1500,
        system=JUDGE_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "judge returned non-JSON", "raw": text}


def main():
    cases = json.loads((ROOT / "evals" / "cases.json").read_text())
    report = []
    for case in cases:
        print(f"→ {case['id']} ({case['skill']})")
        try:
            response = run_agent(case)
            verdict = judge(case, response)
            report.append({"case": case, "response": response, "verdict": verdict})
            score = verdict.get("overall_score", "?")
            print(f"  score: {score}")
        except Exception as e:
            report.append({"case": case, "error": str(e)})
            print(f"  ERROR: {e}")

    out = ROOT / "evals" / "report.json"
    out.write_text(json.dumps(report, indent=2))

    scores = [r["verdict"].get("overall_score", 0) for r in report if "verdict" in r and "overall_score" in r.get("verdict", {})]
    if scores:
        print(f"\nMean score: {sum(scores)/len(scores):.1f} / 10 across {len(scores)} cases")
    print(f"Full report: {out}")


if __name__ == "__main__":
    main()
