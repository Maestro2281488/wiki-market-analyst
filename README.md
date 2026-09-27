# Wiki Market Analyst 📊
> **AI Agent Skill for B2C Product Decision Making using Wikimedia Market Intelligence**  
> Author: **Mykola Shuprovych**  
> Developed for **AI Product Engineering School (Genesis Academy)**  
> Conforming to the [Agent Skills Specification](https://agentskills.io/specification).

---

## 🚀 Overview

B2C product teams (EdTech, Fitness, Language Learning, Utilities) face continuous capital allocation dilemmas:
- *Which topic or course should we launch next?*
- *Which foreign language market has genuine demand vs. vanity hype?*
- *Is user interest organically growing, or was it just a one-off news spike?*

**Wiki Market Analyst** is an autonomous AI agent skill that translates Wikipedia organic traffic (`agent=user`) and Wikidata semantic graphs into high-conviction product decisions. It generates clean multi-market charts and single-page executive PDF reports ready to share with founders and investors.

---

## 📁 Repository Structure

```text
wikimedia_tools/
├── wiki_market_analyst/
│   ├── SKILL.md                  # Standard Agent Skill specification & prompt guidelines
│   ├── requirements.txt          # Minimal reproducible dependencies
│   ├── pyproject.toml            # Packaging configuration
│   ├── main.py                   # ⭐ SINGLE ENTRY POINT CLI for AI agents
│   ├── core/
│   │   ├── __init__.py
│   │   ├── resolver.py           # Cross-lingual topic resolution via Wikidata & Wikipedia
│   │   ├── analyzer.py           # Traffic fetching, 30-day MA smoothing, YoY growth & Trust scoring
│   │   ├── visualizer.py         # Multi-panel Matplotlib comparison charts
│   │   └── reporter.py           # Single-page executive PDF generator (fpdf2 + Unicode fonts)
│   └── tests/
│       ├── __init__.py
│       └── test_scenarios.py     # Automated test suite for all case scenarios
├── docs/
│   ├── ARCHITECTURE.md           # System architecture, data flow & statistical models
│   ├── VERIFICATION_REPORT.md    # End-to-end scenario verification & lightweight LLM benchmarking
│   └── FUTURE_ROADMAP.md         # Scaling roadmap: topic clustering, triangulation & DuckDB
├── output/                       # Generated charts and executive PDFs
└── README.md
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- No compiled binary dependencies; pure Python setup.

### 2. Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# (Linux / macOS: source .venv/bin/activate)

# Install dependencies
pip install -r wiki_market_analyst/requirements.txt
```

---

## 💻 CLI Usage (Single Entry Point for Agents)

The skill provides a deterministic, single-command entry point designed for tool-calling agents (e.g., Claude Haiku 4.5, Gemini Flash, GPT-4o-mini):

```bash
python wiki_market_analyst/main.py --topic "<TOPIC>" --langs "<LANG_CODES>" [--years <YEARS>] [--output-dir <DIR>]
```

### Example Commands:

#### 1. Intermittent Fasting (Poland vs Czechia, 2 Years)
```bash
python wiki_market_analyst/main.py --topic "Intermittent fasting" --langs "pl,cs" --years 2 --output-dir "output/scenario_1"
```

#### 2. Astronomy Course Viability in Ukrainian Wikipedia
```bash
python wiki_market_analyst/main.py --topic "Астрономія" --langs "uk" --years 2 --output-dir "output/scenario_2"
```

#### 3. Language Learning App Localization (5 Languages)
```bash
python wiki_market_analyst/main.py --topic "English language" --langs "uk,pl,es,de,cs" --years 2 --output-dir "output/scenario_3"
```

---

## 🧪 Running Automated Tests

Run the full automated test suite verifying all 3 scenarios:

```bash
python -m unittest wiki_market_analyst/tests/test_scenarios.py
```
*Executes all 3 scenarios end-to-end and validates outputs in ~5 seconds.*

---

## 📈 Key Metrics & Methodology

1. **Bot Filtering:** Explicitly queries `agent=user` via Wikimedia REST API, eliminating web scrapers.
2. **Noise Reduction:** Applies a 30-day Rolling Moving Average to reveal structural baseline trends.
3. **Period Growth (YoY):** Measures percentage shift between observation halves.
4. **Spike Ratio ($\text{Max} / \text{Mean}$):** Detects news-driven viral anomalies ($> 5\times$).
5. **Data Trust Score ($0–100\%$):** Penalizes low volume, high volatility, and spike dominance to protect product teams from acting on misleading signals.

---

## 📑 Generated Artifacts

For each run, the skill produces:
- **Compact JSON:** Structured metrics and executive bullet points printed to stdout (~350 tokens, ideal for budget LLMs).
- **`chart.png`:** Presentation-grade visual comparing trajectories, growth, and trust scores.
- **`report.pdf`:** Sleek, single-page executive PDF report tailored for founders and stakeholders.

---

## 📚 Documentation Links
- [Skill Specification (`SKILL.md`)](file:///wiki_market_analyst/SKILL.md)
- [Cross-Environment & Model Testing Guide](file:///docs/CROSS_ENVIRONMENT_AND_MODEL_TESTING.md)
- [System Architecture & Mathematics](file:///docs/ARCHITECTURE.md)
- [Verification Report & Fast Model Benchmarks](file:///docs/VERIFICATION_REPORT.md)
- [Future Scaling Roadmap](file:///docs/FUTURE_ROADMAP.md)

