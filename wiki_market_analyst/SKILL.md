---
name: wiki-market-analyst
description: Analyze Wikimedia pageviews, evaluate audience interest trends across languages, and generate executive 1-page PDF reports for B2C product decisions.
version: 1.0.0
author: Genesis AI Product Engineering School
tags: [wikimedia, market-research, b2c, trend-analysis, pageviews, localization, edtech]
---

# Wiki Market Analyst Skill

The **Wiki Market Analyst** skill empowers AI agents to perform rigorous, cross-market demand intelligence using Wikipedia Pageviews and Wikidata APIs. It transforms raw organic traffic data into actionable B2C product recommendations, visual trend comparisons, and single-page executive PDF reports.

## When to Use This Skill

Activate this skill when a founder, PM, or strategist asks:
- **Topic Expansion / Course Viability**: "Should we launch an Astronomy course or a Breathwork module in our app?"
- **Market Localization**: "Which languages should we translate our fitness/language-learning product into next?"
- **Trend Verification & Trust**: "Is this topic genuinely growing organically, or is it just transient viral hype / bot traffic?"
- **Cross-Market Comparison**: "Compare user interest in Intermittent Fasting between Poland and Czechia over the past 2 years."

---

## Single Entry Point (CLI)

The skill features a **unified single entry point** (`main.py`) designed specifically for tool-calling agents. The model executes one shell command, and the underlying pipeline automatically performs topic resolution, traffic extraction, noise filtering, moving average smoothing, trust scoring, chart plotting, and PDF generation.

### Execution Command

```bash
python wiki_market_analyst/main.py --topic "<TOPIC>" --langs "<LANG_CODES>" [--years <YEARS>] [--output-dir <DIR>]
```

### CLI Arguments

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--topic` | string | **Required** | The topic or concept query (e.g. `"Intermittent fasting"`, `"Астрономія"`, `"English language"`). Supports any language. |
| `--langs` | string | `"en"` | Comma-separated ISO language codes (e.g. `"pl,cs"`, `"uk"`, `"uk,pl,es,de,cs"`). |
| `--years` | integer | `2` | Historical observation window in years (default: 2 years). |
| `--output-dir` | string | `"output"` | Target directory where `chart.png` and `report.pdf` will be saved. |
| `--no-pdf` | flag | `false` | Skip PDF generation if only quick JSON metrics are needed. |
| `--no-chart` | flag | `false` | Skip Chart generation. |

---

## Machine-Readable JSON Output

`main.py` returns a concise, token-efficient JSON response (typically ~350 tokens) to stdout:

```json
{
  "topic": "Intermittent fasting",
  "resolved_label": "intermittent fasting",
  "qid": "Q1666254",
  "time_window_years": 2,
  "date_range": {
    "start": "2024-09-25",
    "end": "2026-09-25"
  },
  "executive_summary": [
    "Declining / Stagnant Trend: All observed locales exhibit negative or flat growth. Top volume in CS (280 views/mo, -53.9% YoY).",
    "Data Reliability Alert: High volatility or viral spikes detected in CS. Signals reflect transient media hype rather than stable recurring interest.",
    "Content Void: PL has no dedicated Wikipedia page. Represents unaddressed educational demand or low top-of-funnel search awareness."
  ],
  "markets": {
    "pl": {
      "has_data": false,
      "title": null,
      "reason": "No dedicated article in pl.wikipedia.org (only passing mentions, e.g. in 'Stres oksydacyjny')",
      "total_views": 0,
      "monthly_avg": 0,
      "growth_rate_pct": 0.0,
      "trust_score": 0,
      "trust_level": "NONE",
      "recommendation": "Missing Article (Market Void / Low Wikipedia Awareness)"
    },
    "cs": {
      "has_data": true,
      "total_views": 6699,
      "monthly_avg": 280,
      "growth_rate_pct": -53.9,
      "volatility_cv": 2.33,
      "spike_ratio": 55.2,
      "trust_score": 40,
      "trust_level": "LOW",
      "penalties": [
        "Modest search volume (< 5k/year)",
        "Extreme single-day spike (55.2x of average)",
        "High traffic volatility (unstable daily demand)"
      ],
      "recommendation": "Hype-Driven / High Anomaly Risk",
      "title": "Přerušovaný půst",
      "article_url": "https://cs.wikipedia.org/wiki/P%C5%99eru%C5%A1ovan%C3%BD_p%C5%AFst"
    }
  },
  "artifacts": {
    "chart_png": "/path/to/output/chart.png",
    "report_pdf": "/path/to/output/report.pdf"
  }
}
```

---

## Agent Interpretation Guidelines

When explaining results to founders or product leaders, follow these principles:

1. **Decouple Growth from Trust**:
   - High Growth + Low Trust = **Event-driven Hype / PR spike**. Do NOT commit product engineering resources without external validation (search volume / ads testing).
   - High Growth + High Trust = **Greenfield Opportunity**. Strong organic baseline expansion.
   - Low Growth + High Trust = **Evergreen Core**. Mature baseline market (e.g. English learning in Germany).
2. **Handle Missing Articles as Strategic Signals**:
   - If `has_data: false` because no dedicated article exists (e.g., Polish Wikipedia for Intermittent Fasting), explain the duality:
     - *Risk:* Low spontaneous encyclopedic search volume.
     - *Opportunity:* Uncontested content gap where product-led SEO or localized landing pages can capture early-mover advantage.
3. **Point to Generated Artifacts**:
   - Always inform the user that a clean comparison chart (`chart.png`) and an executive 1-page PDF (`report.pdf`) have been compiled and are ready to share with stakeholders.

---

## Common Scenarios & Examples

### Scenario 1: Intermittent Fasting (Poland vs Czechia)
```bash
python wiki_market_analyst/main.py --topic "Intermittent fasting" --langs "pl,cs" --years 2 --output-dir "output/scenario_1"
```
*Takeaway:* Czechia has a dedicated article with modest interest that suffered a sharp post-hype decline (-53.9% YoY) and extreme spike volatility (55x). Poland lacks a dedicated article entirely. Neither market currently demonstrates healthy, steady organic demand.

### Scenario 2: Astronomy Course Viability (Ukrainian Wikipedia)
```bash
python wiki_market_analyst/main.py --topic "Астрономія" --langs "uk" --years 2 --output-dir "output/scenario_2"
```
*Takeaway:* Readership is completely clean and organic (Trust Score 100/100, no bot distortion or fake spikes), but volume is in steady decline (-55.4% YoY). Sponsoring or building a mass standalone Astronomy course is high risk.

### Scenario 3: English Learning App Localization (Multi-Market)
```bash
python wiki_market_analyst/main.py --topic "English language" --langs "uk,pl,es,de,cs" --years 2 --output-dir "output/scenario_3"
```
*Takeaway:* Spanish (`es`) provides the highest top-of-funnel volume (30.5k views/mo), while German (`de`) provides the most resilient baseline (-8.6% YoY, lowest volatility 0.16). Prioritize Spanish for scale and German for high-retention willingness-to-pay cohorts.
