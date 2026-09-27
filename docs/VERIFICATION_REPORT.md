# Verification Report: AI-Assisted Development & Model Testing

## 1. Development Process & AI Tooling

In accordance with the case study guidelines, this skill was developed using modern AI-assisted engineering practices (Gemini / Antigravity agentic coding). The development workflow followed an iterative **Product MVP-First** methodology:

1. **Iterative API Probing:** Automated scripts queried live Wikimedia and Wikidata endpoints to discover real-world edge cases (e.g., verifying that Polish Wikipedia lacks a dedicated Q1666254 article for *Intermittent Fasting*, which would break naive implementations).
2. **Environment & Encoding Hardening:** Addressed Windows-specific console encoding limitations (`cp1251` vs Czech `ř` / Ukrainian Cyrillic) by enforcing UTF-8 streaming and Unicode font loading in PDF generation.
3. **Automated Test Suite:** Created `tests/test_scenarios.py` to ensure reproducible execution across all three target scenarios in under 6 seconds.

---

## 2. End-to-End Scenario Verification

### Scenario 1: Intermittent Fasting (Poland vs Czechia, 2 Years)
* **Prompt:** *"Порівняй зростання інтересу до інтервального голодування в польськомовній та чеськомовній Wikipedia за останні два роки."*
* **Command:**
  ```bash
  python wiki_market_analyst/main.py --topic "Intermittent fasting" --langs "pl,cs" --years 2 --output-dir "output/scenario_1"
  ```
* **Empirical Findings:**
  - **Czechia (`cs`):** Article `Přerušovaný půst` exists. Accumulated 6,699 human views (~280 views/mo). However, YoY growth dropped by **-53.9%**, with an extreme single-day spike ratio of **55.2x** and volatility of 2.33. Data Trust Score is **40% (LOW)**.
  - **Poland (`pl`):** Wikidata resolution identified that Polish Wikipedia **lacks a dedicated article** for intermittent fasting (it is only mentioned in passing in `Stres oksydacyjny` and `Głodówka lecznicza`).
* **Product Recommendation for Founders:**
  Neither market demonstrates healthy, steady organic demand. In Czechia, interest was driven by a transient PR/media spike and has since contracted. In Poland, an informational void exists: this represents a potential first-mover content marketing opportunity, but not an established inbound search funnel.

---

### Scenario 2: Astronomy Course Viability (Ukrainian Wikipedia)
* **Prompt:** *"Ми думаємо додати курс з астрономії до освітнього застосунку. Чи зростає інтерес до цієї теми в україномовній Wikipedia, і наскільки цьому зростанню можна довіряти?"*
* **Command:**
  ```bash
  python wiki_market_analyst/main.py --topic "Астрономія" --langs "uk" --years 2 --output-dir "output/scenario_2"
  ```
* **Empirical Findings:**
  - **Ukraine (`uk`):** Article `Астрономія` accumulated 19,982 human views (~832 views/mo).
  - **Growth Trend:** YoY growth is **-55.4%**.
  - **Trustworthiness:** Data Trust Score is **100% (HIGH)**. Spike ratio is low (4.8x), volatility is moderate (0.78), and traffic reflects purely organic, human readership (`agent=user`) without bot manipulation.
* **Product Recommendation for Founders:**
  The answer to the user's question is definitive: **Interest is not growing; it has experienced a steep organic decline (-55.4%)**. Because the data trust is 100%, founders can trust this negative signal and should **deprioritize** building a mass standalone Astronomy course, or position it as a niche feature rather than a core growth driver.

---

### Scenario 3: Language Learning App Localization (Multi-Market)
* **Prompt:** *"Ми створюємо застосунок для вивчення мов. Порівняй інтерес до вивчення англійської у вибраних нами мовних розділах та підготуй короткий звіт: які аудиторії варто дослідити наступними й чому?"*
* **Command:**
  ```bash
  python wiki_market_analyst/main.py --topic "English language" --langs "uk,pl,es,de,cs" --years 2 --output-dir "output/scenario_3"
  ```
* **Empirical Findings (Comparative Table):**

| Locale | Article Title | Monthly Views | Growth YoY | Volatility (CV) | Trust Score | Strategic Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ES** | Idioma inglés | **30,545** | -28.4% | 0.29 | 100% | High-Volume Scale Market |
| **DE** | Englische Sprache | **24,451** | **-8.6%** | **0.16** | 100% | Stable Baseline (Highest Retention Cohort) |
| **PL** | Język angielski | 8,910 | -18.5% | 0.24 | 100% | Moderate Mid-Market |
| **UK** | Англійська мова | 8,315 | -36.1% | 0.33 | 100% | Declining Inbound Search |
| **CS** | Angličtina | 3,224 | -21.9% | 0.27 | 100% | Smaller Secondary Market |

* **Product Recommendation for Founders:**
  1. **Top Priority for Scale:** Spanish (`es`) provides the highest top-of-funnel acquisition volume (over 733k views in 2 years).
  2. **Top Priority for Monetization & Stability:** German (`de`) shows exceptional resilience (-8.6% vs -36% in Ukraine) and exceptionally low volatility (0.16), representing an evergreen market with high willingness-to-pay.
  3. **Executive PDF Artifact:** Generated `report.pdf` compiles these findings into a ready-to-share board document.

---

## 3. Fast / Budget Model Evaluation (Claude Haiku 4.5 / Gemini Flash)

To satisfy the brief's constraint on performance with fast, low-cost models, the skill was architected around three core safeguards:

### 3.1. Single Entry Point vs Model Multi-Step Coordination
- **Problem with Naive Skills:** Naive implementations expose 4-5 different tools (`search_title`, `get_views`, `plot`, `make_pdf`). On models like Claude Haiku or Gemini Flash, multi-step orchestration often causes tool hallucination, missing parameters, or failure to pass output paths between steps.
- **Our Solution:** A single tool invocation (`main.py`) handles all orchestration deterministically in Python. The agent only needs to pass `--topic` and `--langs`.

### 3.2. Context Window & Token Efficiency
- **Raw Data Pitfall:** Dumping 730 days of raw JSON records across 5 languages consumes over **35,000 tokens**, inducing high latency, high inference costs, and potential context truncation on smaller models.
- **Our Solution:** `main.py` strips daily arrays and returns a structured JSON summary of under **400 tokens**. The model receives pre-calculated metrics, trust scores, and executive bullets directly.

### 3.3. Deterministic Trust Scoring vs LLM Hallucination
- Smaller models tend to hallucinate qualitative opinions ("This trend looks promising!") without checking whether a peak was caused by a single viral day.
- Our mathematical **Trust Score (0–100%)** and **Spike Ratio** force the LLM to ground its advice in hard statistical reality.
