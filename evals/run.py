"""
Eval runner for Claims Copilot.

Fully local — no API keys needed. Uses Ollama for both the agent and the judge.

  Agent model : deepseek-r1:7b  (runs the claims tasks)
  Judge model : deepseek-r1:7b  (scores the outputs against expectations)

For each case in cases.json it:
  1. Builds the context (AGENT.md + relevant skill + all knowledge files).
  2. Runs the agent on the case input.
  3. Strips <think> blocks from the agent response.
  4. Asks the judge to score the clean response against the expectations in JSON.
  5. Writes a full report to evals/report.json.

Usage:
    pip install ollama
    ollama pull deepseek-r1:7b
    python evals/run.py

Optional flags:
    --agent-model  deepseek-r1:1.5b   use a faster/smaller agent model
    --judge-model  deepseek-r1:7b     override the judge model
    --cases        evals/cases.json   path to a different cases file
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import ollama
except ImportError:
    print("Install: pip install ollama")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DEFAULT_MODEL = "deepseek-r1:7b"


# ── Context builder ──────────────────────────────────────────────────────────

def load_context(skill: str, agent_model: str) -> str:
    """AGENT.md + skill playbook + all knowledge files → single system prompt."""
    parts = ["# AGENT\n\n" + (ROOT / "AGENT.md").read_text()]

    skill_map = {
        "triage":   "triage-claim.md",
        "coverage": "coverage-check.md",
        "letter":   "draft-letter.md",
        "summary":  "summarize-file.md",
        "any":      None,
    }
    skill_file = skill_map.get(skill)
    if skill_file:
        parts.append("# ACTIVE SKILL\n\n" + (ROOT / "skills" / skill_file).read_text())

    for p in sorted((ROOT / "knowledge").rglob("*.md")):
        parts.append(f"# KNOWLEDGE — {p.relative_to(ROOT)}\n\n" + p.read_text())

    return "\n\n---\n\n".join(parts)


def strip_think(text: str) -> str:
    """Remove <think>...</think> blocks that deepseek-r1 emits."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# ── Agent ────────────────────────────────────────────────────────────────────

def run_agent(case: dict, agent_model: str) -> str:
    system = load_context(case["skill"], agent_model)
    resp = ollama.chat(
        model=agent_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": case["input"]},
        ],
    )
    return strip_think(resp["message"]["content"])


# ── Judge ────────────────────────────────────────────────────────────────────

JUDGE_SYSTEM = """You are an evaluator for an AI claims-handler assistant.

You will be given:
- The input the agent received
- A list of expectations (things the response should do)
- The agent's response

Score each expectation as PASS or FAIL with a one-line reason.
Then give an overall_score (0-10), a one-sentence summary, and the most important issue (or "none").

YOU MUST RESPOND ONLY WITH VALID JSON. No preamble, no markdown fences. Example:
{
  "per_expectation": [
    {"expectation": "flags vulnerability signal", "verdict": "PASS", "reason": "Agent mentioned distress and suggested slower pace."}
  ],
  "overall_score": 8,
  "summary": "Response handled the case well but missed the police report requirement.",
  "most_important_issue": "Did not mention the need for a police report per §4.4."
}"""


def judge(case: dict, response: str, judge_model: str) -> dict:
    user_msg = (
        f"CASE INPUT:\n{case['input']}\n\n"
        f"EXPECTATIONS:\n{json.dumps(case['expectations'], indent=2)}\n\n"
        f"AGENT RESPONSE:\n{response}"
    )
    resp = ollama.chat(
        model=judge_model,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user",   "content": user_msg},
        ],
        format="json",   # Ollama JSON mode — forces valid JSON output
    )
    raw = strip_think(resp["message"]["content"])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "judge returned non-JSON", "raw": raw}


# ── Runner ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Claims Copilot eval runner (fully local)")
    parser.add_argument("--agent-model", default=DEFAULT_MODEL, help="Ollama model for the agent")
    parser.add_argument("--judge-model", default=DEFAULT_MODEL, help="Ollama model for the judge")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "cases.json"), help="Path to cases JSON")
    args = parser.parse_args()

    cases = json.loads(Path(args.cases).read_text())
    print(f"Agent: {args.agent_model}  |  Judge: {args.judge_model}  |  Cases: {len(cases)}\n")

    report = []
    scores = []

    for case in cases:
        print(f"→ {case['id']} ({case['skill']})", end="  ", flush=True)
        try:
            response = run_agent(case, args.agent_model)
            verdict  = judge(case, response, args.judge_model)
            report.append({"case": case, "response": response, "verdict": verdict})
            score = verdict.get("overall_score")
            if isinstance(score, (int, float)):
                scores.append(score)
                print(f"score: {score}/10")
            else:
                print("score: ?")
        except Exception as e:
            report.append({"case": case, "error": str(e)})
            print(f"ERROR: {e}")

    out = ROOT / "evals" / "report.json"
    out.write_text(json.dumps(report, indent=2))

    if scores:
        print(f"\nMean score : {sum(scores)/len(scores):.1f} / 10  ({len(scores)}/{len(cases)} cases scored)")
    print(f"Report     : {out}")


if __name__ == "__main__":
    main()
