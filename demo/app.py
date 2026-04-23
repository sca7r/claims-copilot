"""
Claims Copilot — Streamlit demo.
Usage:
    pip install streamlit ollama
    streamlit run demo/app.py
"""
import re
from pathlib import Path
import streamlit as st
import ollama

ROOT = Path(__file__).parent.parent

MODELS = {
    "deepseek-r1:1.5b  (fastest)": "deepseek-r1:1.5b",
    "deepseek-r1:7b    (balanced)": "deepseek-r1:7b",
    "deepseek-r1:14b   (best quality)": "deepseek-r1:14b",
}

SKILLS = {
    "Triage a claim": "triage-claim.md",
    "Coverage check": "coverage-check.md",
    "Draft a letter": "draft-letter.md",
    "Summarize a file": "summarize-file.md",
}

# Map policy number prefixes to their wording files
POLICY_FILES = {
    "MOT": "motor_policy.md",
    "HOM": "home_policy.md",
    "TRV": "travel_policy.md",
}

TYPING_INDICATOR = """
<style>
.typing-dots { display:inline-flex; align-items:center; gap:5px; padding:10px 4px; }
.typing-dots span {
    width:9px; height:9px; border-radius:50%;
    background:#888; display:inline-block;
    animation: typing-bounce 1.2s infinite ease-in-out;
}
.typing-dots span:nth-child(1) { animation-delay: 0s; }
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing-bounce {
    0%, 60%, 100% { transform: translateY(0); background: #aaa; }
    30%            { transform: translateY(-6px); background: #555; }
}
</style>
<div class="typing-dots"><span></span><span></span><span></span></div>
"""


def detect_policy_type(text: str) -> str | None:
    """
    Look for a policy number prefix (MOT-..., HOM-..., TRV-...) in the user's input.
    Returns the prefix string or None if not found.
    """
    match = re.search(r'\b(MOT|HOM|TRV)-\S+', text, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def build_system_prompt(skill_file: str, policy_prefix: str | None) -> tuple[str, list[str]]:
    """
    Assembles the context window. If a policy prefix is detected, only loads
    the matching policy wording instead of all three — reduces hallucination.
    Returns (prompt, list of loaded file names for display).
    """
    parts = [(ROOT / "AGENT.md").read_text()]
    parts.append("# ACTIVE SKILL\n\n" + (ROOT / "skills" / skill_file).read_text())

    loaded_files = ["AGENT.md", f"skills/{skill_file}"]

    # Always load non-policy knowledge
    for fname in ["glossary.md", "regulatory.md", "style.md"]:
        p = ROOT / "knowledge" / fname
        if p.exists():
            parts.append(f"# KNOWLEDGE — {fname}\n\n" + p.read_text())
            loaded_files.append(f"knowledge/{fname}")

    # Load only the relevant policy wording, or all if unknown
    policy_dir = ROOT / "knowledge" / "policy wording"
    if policy_prefix and policy_prefix in POLICY_FILES:
        fname = POLICY_FILES[policy_prefix]
        p = policy_dir / fname
        if p.exists():
            parts.append(f"# POLICY WORDING — {fname}\n\n" + p.read_text())
            loaded_files.append(f"knowledge/policy wording/{fname}")
    else:
        for p in sorted(policy_dir.glob("*.md")):
            parts.append(f"# POLICY WORDING — {p.name}\n\n" + p.read_text())
            loaded_files.append(f"knowledge/policy wording/{p.name}")

    return "\n\n---\n\n".join(parts), loaded_files


def stream_response(model: str, system: str, user_input: str):
    """
    Stream tokens from Ollama, separating <think> blocks from the answer.
    Yields (token, is_thinking) tuples.
    """
    in_think = False
    buffer = ""

    stream = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_input},
        ],
        stream=True,
    )

    for chunk in stream:
        token = chunk["message"]["content"]
        buffer += token

        while buffer:
            if not in_think:
                think_start = buffer.find("<think>")
                if think_start == -1:
                    yield buffer, False
                    buffer = ""
                else:
                    if think_start > 0:
                        yield buffer[:think_start], False
                    buffer = buffer[think_start + len("<think>"):]
                    in_think = True
            else:
                think_end = buffer.find("</think>")
                if think_end == -1:
                    yield buffer, True
                    buffer = ""
                else:
                    yield buffer[:think_end], True
                    buffer = buffer[think_end + len("</think>"):]
                    in_think = False


# ── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Claims Copilot", page_icon="📄", layout="wide")
st.title("Claims Copilot")
st.caption("A context-engineering demo for an insurance claims handler. All data synthetic.")

col1, col2 = st.columns([1, 2])

with col1:
    skill_label = st.selectbox("Skill", list(SKILLS.keys()))
    model_label = st.selectbox("Model", list(MODELS.keys()))
    selected_model = MODELS[model_label]

    st.divider()
    show_thinking = st.toggle("Show model reasoning", value=False)
    with st.expander("See AGENT.md"):
        st.code((ROOT / "AGENT.md").read_text(), language="markdown")

with col2:
    user_input = st.text_area(
        "Input (paste an FNOL, facts + wording, or a claim file):",
        height=220,
        placeholder="e.g., 'New FNOL — tree fell on customer's car during overnight storm. Policy number MOT-2024-0192.'",
    )

    if st.button("Run", type="primary", disabled=not user_input.strip()):
        try:
            policy_prefix = detect_policy_type(user_input)
            system, loaded_files = build_system_prompt(SKILLS[skill_label], policy_prefix)

            # Show which files were actually loaded into context
            with col1:
                st.markdown("**Context loaded for this call:**")
                for f in loaded_files:
                    if "policy wording" in f:
                        st.markdown(f"- `{f}` ✅ detected `{policy_prefix}`")
                    else:
                        st.markdown(f"- `{f}`")
                if not policy_prefix:
                    st.caption("No policy prefix detected — all policies loaded.")

            thinking_placeholder = st.empty()
            thinking_text = ""
            answer_text = ""

            st.markdown("### Output")
            answer_placeholder = st.empty()

            answer_placeholder.markdown(TYPING_INDICATOR, unsafe_allow_html=True)
            first_answer_token = True

            for token, is_thinking in stream_response(selected_model, system, user_input):
                if is_thinking:
                    thinking_text += token
                    if show_thinking:
                        thinking_placeholder.info(f"**Thinking…**\n\n{thinking_text}")
                else:
                    if first_answer_token:
                        first_answer_token = False
                    answer_text += token
                    answer_placeholder.markdown(answer_text)

            if show_thinking and thinking_text:
                thinking_placeholder.empty()
                with st.expander("Model reasoning (deepseek-r1 chain of thought)"):
                    st.markdown(thinking_text.strip())
            else:
                thinking_placeholder.empty()

        except Exception as e:
            st.error(f"Error: {e}\n\nMake sure Ollama is running and you've pulled the model:\n`ollama pull {selected_model}`")
