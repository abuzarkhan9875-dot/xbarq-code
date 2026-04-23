import streamlit as st
import subprocess
import tempfile
import os
import re
import json
import requests
from datetime import datetime
from radon.complexity import cc_visit
import plotly.graph_objects as go

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Xbarq Code",
    page_icon="python/xbarq-logo.svg",
    layout="wide"
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5-coder:7b"

# History JSON file — same folder as app.py
HISTORY_FILE = os.path.join(os.path.dirname(__file__), "xbarq_history.json")

# =====================================================
# HISTORY HELPERS
# =====================================================


def load_history():
    """Load history from JSON file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    """Save history to JSON file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def add_to_history(score, errors, complexity, mode):
    """Add a new entry to history."""
    history = load_history()
    entry = {
        "date": datetime.now().strftime("%d %b %Y"),
        "time": datetime.now().strftime("%I:%M %p"),
        "score": score,
        "errors": errors,
        "complexity": complexity,
        "mode": mode,
    }
    history.insert(0, entry)  # newest first
    history = history[:50]    # keep last 50 only
    save_history(history)

# =====================================================
# CHARCOAL BLACK THEME
# =====================================================


st.markdown("""
<style>
.stApp {
    background-color: #121212;
    color: #e5e5e5;
}

section[data-testid="stSidebar"] {
    background-color: #1E1E1E;
    border-right: 1px solid #2a2a2a;
}

.block-container {
    padding-top: 2rem;
}

textarea {
    background-color: #1c1c1c !important;
    color: white !important;
    border-radius: 10px !important;
    border: 1px solid #2a2a2a !important;
    font-family: monospace !important;
}

.stButton>button {
    background: linear-gradient(135deg, #525861 0%, #3a3f47 60%, #2c3038 100%);
    color: #f0f0f0;
    border-radius: 10px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.4px;
    border: 1px solid #6b727d;
    padding: 10px 22px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.07);
    transition: all 0.2s ease;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #5f6670 0%, #454b54 60%, #353a42 100%);
    border-color: #8a9099;
    box-shadow: 0 4px 14px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.1);
    color: #ffffff;
    transform: translateY(-1px);
}

.stButton>button:active {
    transform: translateY(0px);
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

/* Sidebar buttons — monospace font + single line fix */
section[data-testid="stSidebar"] .stButton>button {
    font-family: "IBM Plex Mono", monospace !important;
    white-space: nowrap !important;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: 13px;
    padding: 9px 14px;
}

[data-testid="metric-container"] {
    background-color: #1c1c1c;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #2a2a2a;
}

section[data-testid="stSidebar"] {
    padding-top: 20px;
}

.sidebar-title {
    font-family: "scandia","scandia Fallback",sans-serif;
    font-size: 22px;
    font-weight: 700;
    margin-top: 10px;
    margin-bottom: 5px;
}

.sidebar-subtitle {
    font-family: IBM Plex Mono,monospace;
    font-size: 14px;
    color: #9ca3af;
    margin-bottom: 20px;
}

/* History Card Styling */
.history-card {
    background-color: #1c1c1c;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}

.history-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.history-score {
    font-size: 22px;
    font-weight: 700;
    color: #2563eb;
}

.history-date {
    font-size: 12px;
    color: #9ca3af;
}

.history-badge {
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
}

.badge-fix {
    background-color: #16a34a22;
    color: #4ade80;
    border: 1px solid #16a34a;
}

.badge-review {
    background-color: #2563eb22;
    color: #60a5fa;
    border: 1px solid #2563eb;
}

.badge-fix_failed {
    background-color: #f59e0b22;
    color: #fbbf24;
    border: 1px solid #f59e0b;
}

.history-meta {
    display: flex;
    gap: 16px;
    font-size: 13px;
    color: #9ca3af;
}

/* Sidebar stat cards */
.stat-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 8px;
    margin-bottom: 4px;
}

.stat-card {
    background: linear-gradient(135deg, #1e2025 0%, #25282e 100%);
    border: 1px solid #2e3138;
    border-radius: 10px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.stat-icon {
    font-size: 18px;
    min-width: 24px;
    text-align: center;
}

.stat-info {
    display: flex;
    flex-direction: column;
}

.stat-label {
    font-family: "IBM Plex Mono", monospace;
    font-size: 10px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

.stat-value {
    font-family: "IBM Plex Mono", monospace;
    font-size: 14px;
    font-weight: 700;
    color: #e5e5e5;
}

/* Sidebar history cards */
.sidebar-history-card {
    background: linear-gradient(135deg, #1e2025 0%, #25282e 100%);
    border: 1px solid #2e3138;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
}

.sidebar-history-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.sidebar-history-score {
    font-family: "IBM Plex Mono", monospace;
    font-size: 16px;
    font-weight: 700;
}

.sidebar-history-meta {
    font-family: "IBM Plex Mono", monospace;
    font-size: 10px;
    color: #6b7280;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE INIT
# =====================================================

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "results" not in st.session_state:
    st.session_state.results = None

if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

if "show_history" not in st.session_state:
    st.session_state.show_history = False

# =====================================================
# SIDEBAR
# =====================================================

logo_path = os.path.join(os.path.dirname(__file__), "xbarq-logo.svg")

st.sidebar.image(logo_path, width=80)

st.sidebar.markdown(
    """
    <div class="sidebar-title">Xbarq Code.</div>
    <div class="sidebar-subtitle">AI Powered Code Quality Platform</div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# History Button in Sidebar
if st.sidebar.button("📜 View History", use_container_width=True):
    st.session_state.show_history = not st.session_state.show_history

# Clear History Button
if st.sidebar.button("🗑️ Clear History", use_container_width=True):
    save_history([])
    st.sidebar.success("History cleared!")
    st.rerun()

# ── Stat Cards ──
history = load_history()
st.sidebar.markdown("---")

if history:
    avg = round(sum(h["score"] for h in history) / len(history), 2)
    avg_color = "#4ade80" if avg >= 7 else (
        "#fbbf24" if avg >= 4 else "#f87171")
    last = history[0]
    st.sidebar.markdown(f"""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-icon">🏃</div>
            <div class="stat-info">
                <span class="stat-label">Total Runs</span>
                <span class="stat-value">{len(history)}</span>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
                <span class="stat-label">Avg Score</span>
                <span class="stat-value" style="color:{avg_color};">{avg}/10</span>
            </div>
        </div>
        <div class="stat-card">
            <div class="stat-icon">🕒</div>
            <div class="stat-info">
                <span class="stat-label">Last Run</span>
                <span class="stat-value" style="font-size:11px;">{last['date']} · {last['time']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div class="stat-grid">
        <div class="stat-card">
            <div class="stat-icon">🏃</div>
            <div class="stat-info">
                <span class="stat-label">Total Runs</span>
                <span class="stat-value">0</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── History Panel in Sidebar ──
if st.session_state.show_history:
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📜 Recent History")
    if not history:
        st.sidebar.info("No history yet.")
    else:
        for entry in history[:10]:
            mode = entry.get("mode", "review")
            score = entry["score"]
            score_color = "#4ade80" if score >= 7 else (
                "#fbbf24" if score >= 4 else "#f87171")
            badge = "✅ Fixed" if mode == "fix" else (
                "⭐ Review" if mode == "review" else "⚠️ Partial")
            st.sidebar.markdown(f"""
            <div class="sidebar-history-card">
                <div class="sidebar-history-top">
                    <span class="sidebar-history-score" style="color:{score_color};">{score}/10</span>
                    <span style="font-size:10px;color:#6b7280;">{badge}</span>
                </div>
                <div class="sidebar-history-meta">
                    🕒 {entry['date']} · {entry['time']}<br/>
                    ❌ Errors: {entry['errors']} &nbsp;|&nbsp; 🔁 Complexity: {entry['complexity']}
                </div>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# MAIN UI
# =====================================================

col_logo, col_title = st.columns([1, 10])

with col_logo:
    st.image("python/xbarq-logo.svg", width=90)

with col_title:
    st.markdown(
        "<h1 style='margin-bottom:70px; margin-right:130px; font-family: var(--font-scandia),sans-serif'>Python Code Analyzer.</h1>",
        unsafe_allow_html=True
    )

# =====================================================
# FILE UPLOAD + CODE INPUT
# =====================================================

uploaded_files = st.file_uploader(
    "Upload Python Files",
    type=["py"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.reset_counter}"
)

st.markdown("### Or Write Code")

code_input = st.text_area(
    "",
    height=300,
    key=f"code_input_{st.session_state.reset_counter}"
)

colA, colB = st.columns([4, 1])

with colA:
    analyze_button = st.button("Analyze Code")

with colB:
    reset_button = st.button("Reset")

if reset_button:
    st.session_state.reset_counter += 1
    st.session_state.show_results = False
    st.session_state.results = None
    st.rerun()

# =====================================================
# PYLINT SCORE HELPER
# =====================================================


def get_pylint_score(code_content):
    """Run pylint on code and return score + output."""
    try:
        compile(code_content, "<string>", "exec")
    except SyntaxError:
        return 0.0, "Syntax Error in code."

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp:
        temp.write(code_content)
        temp_path = temp.name

    result = subprocess.run(
        ["pylint", temp_path, "--score=y"],
        capture_output=True,
        text=True
    )
    os.remove(temp_path)

    pylint_output = result.stdout
    score_match = re.search(r"rated at ([\d\.]+)/10", pylint_output)
    score = float(score_match.group(1)) if score_match else 0.0
    return score, pylint_output

# =====================================================
# EXTRACT PYTHON CODE FROM AI RESPONSE
# =====================================================


def extract_python_code(raw_response):
    """Extract only Python code from AI response."""
    match = re.search(r"```(?:python)?\n?(.*?)```", raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()

    lines = raw_response.splitlines()
    python_keywords = (
        "import ", "from ", "def ", "class ", "#", "if ",
        "for ", "while ", "try:", "with ", "return ", "print(", "@"
    )
    for i, line in enumerate(lines):
        if any(line.strip().startswith(kw) for kw in python_keywords):
            return "\n".join(lines[i:]).strip()

    return raw_response.strip()

# =====================================================
# ITERATIVE AI CODE FIXER
# =====================================================


def ai_fix_code_iteratively(code_content, pylint_output, original_score, target_score=7.0, max_iterations=4):
    """Iteratively fix code using AI until score >= target or max iterations."""

    current_code = code_content
    current_pylint = pylint_output
    current_score = original_score
    best_code = None
    best_score = original_score
    best_pylint = pylint_output

    for _ in range(1, max_iterations + 1):
        prompt = (
            "You are an expert Python developer specializing in clean, pylint-compliant code.\n\n"
            f"This Python code currently scores {current_score}/10 on pylint. "
            f"Your goal is to fix it to score {target_score}+ out of 10.\n\n"
            "FIX THESE ISSUES:\n"
            "- Add docstrings to ALL functions, classes, and the module\n"
            "- Fix ALL naming convention issues (use snake_case)\n"
            "- Remove ALL unused imports\n"
            "- Fix line length issues (max 100 chars per line)\n"
            "- Add proper spacing between functions (2 blank lines)\n"
            "- Fix ALL other pylint warnings and errors listed below\n\n"
            "RULES:\n"
            "- Keep the EXACT same logic and functionality\n"
            "- Do NOT add new features\n"
            "- Do NOT add any explanation text\n"
            "- Do NOT use markdown or triple backticks\n"
            "- Start your response DIRECTLY with Python code\n\n"
            f"=== CURRENT PYLINT ISSUES (Score: {current_score}/10) ===\n"
            f"{current_pylint}\n\n"
            f"=== PYTHON CODE TO FIX ===\n"
            f"{current_code}\n\n"
            "=== FIXED PYTHON CODE ==="
        )

        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                timeout=120
            )
            raw = response.json().get("response", "").strip()
            fixed_code = extract_python_code(raw)

            try:
                compile(fixed_code, "<string>", "exec")
            except SyntaxError:
                continue

            new_score, new_pylint = get_pylint_score(fixed_code)

            if new_score > best_score:
                best_code = fixed_code
                best_score = new_score
                best_pylint = new_pylint

            current_code = fixed_code
            current_pylint = new_pylint
            current_score = new_score

            if new_score >= target_score:
                break

        except Exception:
            continue

    if best_code and best_score > original_score:
        return best_code, best_score, best_pylint, True
    elif best_code:
        return best_code, best_score, best_pylint, False
    else:
        return None, original_score, pylint_output, False

# =====================================================
# MAIN ANALYZE FUNCTION
# =====================================================


def analyze_code(code_content):
    """Analyze code and return results."""
    try:
        compile(code_content, "<string>", "exec")
    except SyntaxError as e:
        return (0, f"Syntax Error:\n{e}", 1, 0, "review", "❌ Fix syntax errors before AI analysis.", None, None)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w", encoding="utf-8") as temp:
        temp.write(code_content)
        temp_path = temp.name

    result = subprocess.run(
        ["pylint", temp_path, "--score=y"],
        capture_output=True,
        text=True
    )
    os.remove(temp_path)

    pylint_output = result.stdout
    score_match = re.search(r"rated at ([\d\.]+)/10", pylint_output)
    score = float(score_match.group(1)) if score_match else 0.0
    error_count = pylint_output.lower().count("error")

    try:
        complexity_blocks = cc_visit(code_content)
        avg_complexity = (
            round(sum(c.complexity for c in complexity_blocks) /
                  len(complexity_blocks), 2)
            if complexity_blocks else 0
        )
    except:
        avg_complexity = 0

    if score >= 7:
        prompt = (
            "You are a senior Python code reviewer.\n\n"
            f"This code has an excellent Pylint score of {score}/10.\n\n"
            "Write a positive and encouraging review in 3 sections:\n"
            "1. ✅ What is done really well in this code\n"
            "2. 🌟 Why this code is clean and maintainable\n"
            "3. 💡 Any minor optional suggestions (if any) to make it even better\n\n"
            "Python Code:\n"
            f"{code_content}\n\n"
            "RULES:\n"
            "- Write in plain English only.\n"
            "- Be positive, encouraging and professional.\n"
            "- Do NOT output any Python code or code blocks.\n"
        )
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                timeout=60
            )
            ai_review = response.json().get("response", "No AI response received.")
        except Exception as e:
            ai_review = f"⚠️ AI connection error: {str(e)}"

        return score, pylint_output, error_count, avg_complexity, "review", ai_review, None, None

    else:
        fixed_code, new_score, new_pylint, success = ai_fix_code_iteratively(
            code_content, pylint_output, score, target_score=7.0, max_iterations=4
        )
        if success:
            return score, pylint_output, error_count, avg_complexity, "fix", fixed_code, new_score, new_pylint
        elif fixed_code:
            return score, pylint_output, error_count, avg_complexity, "fix_failed", fixed_code, new_score, new_pylint
        else:
            return score, pylint_output, error_count, avg_complexity, "error", "⚠️ AI could not fix the code after multiple attempts.", None, None


# =====================================================
# RUN ANALYSIS
# =====================================================

if analyze_button:

    combined_code = ""

    if uploaded_files:
        for file in uploaded_files:
            combined_code += file.read().decode("utf-8") + "\n\n"

    if code_input:
        combined_code += code_input

    if not combined_code.strip():
        st.warning("No input provided.")
    else:
        with st.spinner("🔍 Analyzing... AI is iteratively fixing bad code to reach 7+ score"):
            results = analyze_code(combined_code)
            st.session_state.results = results
            st.session_state.show_results = True

            # ✅ Save to persistent JSON history
            add_to_history(
                score=results[0],
                errors=results[2],
                complexity=results[3],
                mode=results[4]
            )

# =====================================================
# SHOW RESULTS
# =====================================================

if st.session_state.show_results and st.session_state.results:

    score, pylint_output, errors, complexity, mode, ai_result, new_score, new_pylint = st.session_state.results

    col1, col2, col3 = st.columns(3)
    col1.metric("Pylint Score", f"{score}/10")
    col2.metric("Error Count", errors)
    col3.metric("Avg Complexity", complexity)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': "Code Quality"},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "#2563eb"},
            'steps': [
                {'range': [0, 4], 'color': '#ff4444'},
                {'range': [4, 7], 'color': '#ffaa00'},
                {'range': [7, 10], 'color': '#00cc44'},
            ]
        }
    ))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 📊 Pylint Output")
    st.code(pylint_output)

    if mode == "review":
        st.markdown("## 🤖 AI Review")
        st.success("✅ Great code! Here's what the AI thinks:")
        st.markdown(ai_result)

    elif mode == "fix":
        st.markdown("## 🤖 AI Fixed Your Code")
        st.success(f"✅ Score improved: **{score}/10** → **{new_score}/10**")
        st.code(ai_result, language="python")
        st.markdown("## 📊 Improved Pylint Output")
        st.code(new_pylint)

        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=new_score,
            title={'text': "Improved Code Quality"},
            gauge={
                'axis': {'range': [0, 10]},
                'bar': {'color': "#2563eb"},
                'steps': [
                    {'range': [0, 4], 'color': '#ff4444'},
                    {'range': [4, 7], 'color': '#ffaa00'},
                    {'range': [7, 10], 'color': '#00cc44'},
                ]
            }
        ))
        st.plotly_chart(fig2, use_container_width=True)

    elif mode == "fix_failed":
        st.markdown("## 🤖 AI Best Attempt")
        st.warning(
            f"⚠️ AI improved from **{score}/10** → **{new_score}/10** but couldn't reach 7+.")
        st.code(ai_result, language="python")
        if new_pylint:
            st.markdown("## 📊 Best Attempt Pylint Output")
            st.code(new_pylint)

    elif mode == "error":
        st.markdown("## 🤖 AI Error")
        st.error(ai_result)

    report = f"""
Xbarq Code Analysis Report

Original Score: {score}/10
Errors: {errors}
Complexity: {complexity}

Pylint Output:
{pylint_output}

AI Result ({mode}):
{ai_result}
"""
    if new_score:
        report += f"\nImproved Score: {new_score}/10\nImproved Pylint:\n{new_pylint}"

    st.download_button(
        label="Download Report",
        data=report,
        file_name="xbarq_report.txt"
    )
