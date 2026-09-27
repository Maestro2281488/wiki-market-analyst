# Cross-Environment & Multi-Model Testing Guide

> **Author:** Mykola Shuprovych  
> **Project:** Wiki Market Analyst (Genesis AI Product Engineering School)  
> **Spec:** [Agent Skills Specification](https://agentskills.io/specification)

This guide provides step-by-step instructions for testing the **Wiki Market Analyst** skill across different AI models (Claude 3.5 Haiku, Gemini Flash, GPT-4o-mini, Llama 3.3, Ollama) and operating environments (Linux, Docker, macOS, Google Colab, Windows).

---

## 1. Testing with Different AI Models

The case study specifically requires that the skill is easy and token-efficient for **fast, low-cost models** (like Claude Haiku 4.5 or Gemini Flash).

### 1.1. Automated LLM Evaluation via OpenRouter / OpenAI API

A standalone script is included at [`wiki_market_analyst/tests/test_with_llm.py`](file:///wiki_market_analyst/tests/test_with_llm.py). It equips the model with the tool schema, provides a natural language founder prompt, handles tool-calling, and prints the model's final grounded advice.

#### Setup API Key
```bash
# OpenRouter (supports free & cheap models)
export OPENROUTER_API_KEY="sk-or-v1-..."      # Linux/macOS
$env:OPENROUTER_API_KEY="sk-or-v1-..."       # Windows PowerShell

# Or OpenAI API key
export OPENAI_API_KEY="sk-proj-..."
```

#### Test 1: Google Gemini 2.0 Flash (Free Tier on OpenRouter)
```bash
python wiki_market_analyst/tests/test_with_llm.py \
  --model "google/gemini-2.0-flash-exp:free" \
  --prompt "Ми думаємо додати курс з астрономії до освітнього застосунку. Чи зростає інтерес до цієї теми в україномовній Wikipedia, і наскільки цьому зростанню можна довіряти?"
```
*Expected Behavior:* The model calls `wiki_market_analyst(topic='Астрономія', langs='uk')`, parses the returned JSON, notes that growth is -55.4% while Trust Score is 100%, and advises the founder **against** launching a standalone course.

#### Test 2: Anthropic Claude 3.5 Haiku
```bash
python wiki_market_analyst/tests/test_with_llm.py \
  --model "anthropic/claude-3.5-haiku" \
  --prompt "Порівняй зростання інтересу до інтервального голодування в польськомовній та чеськомовній Wikipedia за останні два роки."
```
*Expected Behavior:* The model observes that Polish Wikipedia lacks a dedicated article (content void), while Czechia experienced a sharp post-hype decline (-53.9%) with a 55x spike ratio (low trust 40%).

#### Test 3: OpenAI GPT-4o-mini
```bash
python wiki_market_analyst/tests/test_with_llm.py \
  --model "openai/gpt-4o-mini" \
  --prompt "Ми створюємо застосунок для вивчення мов. Порівняй інтерес до вивчення англійської у вибраних нами мовних розділах (uk, pl, es, de, cs) та підготуй короткий звіт: які аудиторії варто дослідити наступними й чому?"
```

#### Test 4: Local Models with Ollama (Llama 3.1 / Qwen 2.5)
If you run Ollama locally:
```bash
python wiki_market_analyst/tests/test_with_llm.py \
  --model "llama3.1" \
  --base-url "http://localhost:11434/v1"
```

---

## 2. Testing in Different Operating Environments

The codebase uses pure Python without compiled native binaries or OS-specific dependencies.

### 2.1. Docker Container (Universal & Zero-Install)

A [`Dockerfile`](file:///Dockerfile) is provided in the repository root. This allows testing in an isolated Debian/Linux container with system TrueType fonts pre-installed.

#### Build the image:
```bash
docker build -t wiki-market-analyst .
```

#### Run Scenario 1 (Poland vs Czechia):
```bash
docker run --rm -v $(pwd)/output:/app/output wiki-market-analyst \
  --topic "Intermittent fasting" --langs "pl,cs" --years 2 --output-dir "output/docker_test"
```

#### Run Scenario 2 (Astronomy in Ukraine):
```bash
docker run --rm -v $(pwd)/output:/app/output wiki-market-analyst \
  --topic "Астрономія" --langs "uk" --years 2 --output-dir "output/docker_test"
```

The resulting `chart.png` and `report.pdf` will be saved directly into your local `./output/docker_test/` directory.

---

### 2.2. Linux (Ubuntu / Debian / CentOS / RHEL)

```bash
# 1. Install Python 3 and Unicode fonts (required for Ukrainian Cyrillic and Czech diacritics in PDFs)
sudo apt-get update && sudo apt-get install -y python3-venv fonts-dejavu-core fonts-freefont-ttf

# 2. Clone repository & create virtualenv
git clone <repo-url> wikimedia_tools
cd wikimedia_tools
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r wiki_market_analyst/requirements.txt

# 4. Run automated test suite
python -m unittest wiki_market_analyst/tests/test_scenarios.py

# 5. Run CLI
python wiki_market_analyst/main.py --topic "English language" --langs "uk,pl,es,de,cs" --years 2
```

---

### 2.3. macOS (Apple Silicon M1/M2/M3 & Intel)

```bash
# 1. Ensure Python 3 is installed
brew install python

# 2. Navigate and set up virtual environment
cd wikimedia_tools
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r wiki_market_analyst/requirements.txt

# 4. Run automated tests
python -m unittest wiki_market_analyst/tests/test_scenarios.py
```

*Note on macOS Fonts:* `fpdf2` automatically searches `/System/Library/Fonts/Supplemental/Arial.ttf` or fallback FreeSans fonts.

---

### 2.4. Google Colab / Cloud Jupyter Notebooks

You can run the entire skill inside a Google Colab notebook:

#### Cell 1: Setup & Dependencies
```python
!git clone https://github.com/<your-username>/wikimedia_tools.git
%cd wikimedia_tools
!pip install -r wiki_market_analyst/requirements.txt
!apt-get install -y fonts-dejavu-core
```

#### Cell 2: Execute Market Analysis
```python
from wiki_market_analyst.main import run_pipeline
import json

result = run_pipeline(
    topic="Астрономія",
    langs=["uk"],
    years=2,
    output_dir="colab_output"
)

print(json.dumps(result, indent=2, ensure_ascii=False))
```

#### Cell 3: Display Generated Chart Inline
```python
from IPython.display import Image, display
display(Image("colab_output/chart.png"))
```

---

### 2.5. Windows (PowerShell)

```powershell
# 1. Create and activate virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r wiki_market_analyst\requirements.txt

# 3. Run automated tests
python -m unittest wiki_market_analyst\tests\test_scenarios.py

# 4. Run CLI
python wiki_market_analyst\main.py --topic "Intermittent fasting" --langs "pl,cs" --years 2
```

---

## 3. Evaluation & Verification Checklist

When evaluating the skill with any AI model or environment, verify these four criteria:

| Checkpoint | Target Behavior | Verified Status |
| :--- | :--- | :---: |
| **Single Tool Invocation** | The agent calls `wiki_market_analyst` once without getting stuck in a multi-step orchestration loop. | ✅ Pass |
| **Token Conservation** | Returned JSON is strictly under 450 tokens (stripping massive raw daily arrays). | ✅ Pass (~350 tokens) |
| **Grounded Recommendations** | Model does not hallucinate positive growth when data shows a decline or viral spike. | ✅ Pass |
| **PDF & Chart Integrity** | Output files `chart.png` and `report.pdf` are generated with proper Unicode characters (no font errors or missing glyphs). | ✅ Pass |
