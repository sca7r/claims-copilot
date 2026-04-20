"""
Claims Copilot — Streamlit demo.

Usage:
    pip install streamlit anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    streamlit run demo/app.py
"""

from pathlib import Path
import streamlit as st
from anthropic import Anthropic

ROOT = Path(__file__).parent.parent
MODEL = "claude-opus-4-7"

SKILLS = {
    "Triage a claim": "triage-claim.md",
    "Coverage check": "coverage-check.md",
    "Draft a letter": "draft-letter.md",
    "Summarize a file": "summarize-file.md",
}


def build_system_prompt(skill_file: str) -> str:
    parts = [(ROOT / "AGENT.md").read_text()]
    parts.append("# ACTIVE SKILL\n\n" + (ROOT / "skills" / skill_file).read_text())
    for p in sorted((ROOT / "knowledge").rglob("*.md")):
        parts.append(f"# KNOWLEDGE — {p.relative_to(ROOT)}\n\n" + p.read_text())
    return "\n\n---\n\n".join(parts)


st.set_page_config(page_title="Claims Copilot", page_icon="📄", layout="wide")
st.title("Claims Copilot")
st.caption("A context-engineering demo for an insurance claims handler. All data synthetic.")

col1, col2 = st.columns([1, 2])

with col1:
    skill_label = st.selectbox("Skill", list(SKILLS.keys()))
    st.markdown("**Context being loaded:**")
    st.markdown("- AGENT.md (role + guardrails)")
    st.markdown(f"- skills/{SKILLS[skill_label]}")
    st.markdown("- knowledge/ (policies, regulatory, style, glossary)")
    st.divider()
    with st.expander("See AGENT.md"):
        st.code((ROOT / "AGENT.md").read_text(), language="markdown")

with col2:
    user_input = st.text_area(
        "Input (paste an FNOL, facts + wording, or a claim file):",
        height=220,
        placeholder="e.g., 'New FNOL — tree fell on customer's car during overnight storm. Policy MOT-2024-0192. Customer uses car for work, wants fast resolution.'",
    )

    if st.button("Run", type="primary", disabled=not user_input.strip()):
        with st.spinner("Thinking…"):
            try:
                client = Anthropic()
                skill_key = {
                    "Triage a claim": "triage",
                    "Coverage check": "coverage",
                    "Draft a letter": "letter",
                    "Summarize a file": "summary",
                }[skill_label]
                system = build_system_prompt(SKILLS[skill_label])
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=2000,
                    system=system,
                    messages=[{"role": "user", "content": user_input}],
                )
                text = "".join(b.text for b in resp.content if b.type == "text")
                st.markdown("### Output")
                st.markdown(text)
            except Exception as e:
                st.error(f"Error: {e}")
