# 🔷 Xbarq Code
### AI Powered Python Code Quality Platform

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-black?style=for-the-badge)
![Pylint](https://img.shields.io/badge/Pylint-Code%20Quality-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

---

## 📌 About

**Xbarq Code** is a local AI-powered Python code quality analyzer built with Streamlit.  
It analyzes your Python code using **Pylint**, measures **cyclomatic complexity**, and uses a local **LLM (qwen2.5-coder:7b)** via Ollama to either:

- ✅ **Review good code** (score ≥ 7) — gives positive, encouraging feedback
- 🔧 **Fix bad code** (score < 7) — iteratively rewrites and improves code until it reaches 7+/10

All processing is **100% local** — no API keys, no internet required for AI.

---

## ✨ Features

- 📊 **Pylint Score Analysis** — instant code quality score out of 10
- 🤖 **AI Code Review** — positive review for clean code
- 🔧 **AI Code Fixer** — iterative fixing for bad code (up to 4 retries)
- 📈 **Cyclomatic Complexity** — measures code complexity
- 🎨 **Gauge Chart** — visual score indicator (red → yellow → green)
- 📜 **Persistent History** — saved to JSON, survives page refresh
- 📁 **File Upload** — analyze `.py` files directly
- 📝 **Code Editor** — write code directly in browser
- ⬇️ **Download Report** — export full analysis as `.txt`
- 🌙 **Dark Theme** — charcoal black professional UI

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| [Streamlit](https://streamlit.io) | Web UI framework |
| [Pylint](https://pylint.org) | Python code linter |
| [Radon](https://radon.readthedocs.io) | Cyclomatic complexity |
| [Ollama](https://ollama.com) | Local LLM runner |
| [qwen2.5-coder:7b](https://ollama.com/library/qwen2.5-coder) | AI code model |
| [Plotly](https://plotly.com) | Gauge chart visualization |

---

## ⚡ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/abuzarkhan9875-dot/xbarq-code.git
cd xbarq-code
```

### 2. Install Python Dependencies

```bash
pip install streamlit pylint radon plotly requests
```

### 3. Install Ollama

Download from: **https://ollama.com/download**

### 4. Pull the AI Model

```bash
ollama pull qwen2.5-coder:7b
```

> ⚠️ Requires ~4.5GB disk space. Recommended: 8GB+ RAM, 6GB GPU VRAM

---

## 🚀 Run the App

```bash
streamlit run test.py
```

Then open your browser at: **http://localhost:8501**

> Make sure Ollama is running in the background before launching.

---

## 🤖 How AI Works

```
Your Code
    │
    ▼
Pylint Analysis
    │
    ├── Score ≥ 7 ──► AI gives positive text review ✅
    │
    └── Score < 7 ──► AI fixes code iteratively 🔧
                          │
                          ▼
                    Run Pylint again
                          │
                          ├── Score ≥ 7 → Done ✅
                          │
                          └── Score < 7 → Retry (max 4x)
```

---

## 📁 Project Structure

```
xbarq-code/
│
├── test.py              # Main Streamlit app
├── xbarq-logo.svg       # App logo
├── xbarq_history.json   # Auto-generated history (gitignored)
├── .gitignore
└── README.md
```

---

## 💻 System Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| GPU VRAM | 4 GB | 6 GB+ |
| Disk Space | 5 GB | 10 GB |
| Python | 3.10+ | 3.13+ |

---

## 📜 License

This project is licensed under the **MIT License** — free to use, modify and distribute.

---

## 👨‍💻 Author

**Abuzar Khan**  
GitHub: [@abuzarkhan9875-dot](https://github.com/abuzarkhan9875-dot)

---

> Built with ❤️ using Streamlit + Ollama — 100% local, 100% private.
