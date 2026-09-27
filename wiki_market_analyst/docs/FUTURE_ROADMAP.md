# Future Roadmap: Iterative Scaling & Advanced Research

This document outlines the strategic engineering roadmap for evolving `wiki-market-analyst` from an MVP single-article analyzer into an enterprise-grade market intelligence platform.

---

## Phase 1: Topic Clustering & Semantic Knowledge Graphs (Near-Term)

### 1.1. Category Tree & Wikidata Graph Traversal
* **Current Limitation:** Analyzes a single central article (e.g. `Астрономія`).
* **Evolution:** Expand topic definitions into **Semantic Topic Clusters**.
  - Using Wikidata SPARQL endpoints (`query.wikidata.org`) and Wikipedia Category trees (`incategory:`), the skill will automatically discover all child concepts (e.g. for *Astronomy*: `Астрофізика`, `Планетологія`, `Телескоп Джеймса Вебба`, `Чорна діра`).
  - Aggregating pageviews across an entire cluster provides a complete measure of category-wide TAM (Total Addressable Market) rather than single-article bias.

### 1.2. Competitive Benchmarking & Share of Voice
* Enable comparative topic sets:
  ```bash
  python main.py --cluster "Diets" --topics "Keto,Intermittent fasting,Mediterranean diet,Vegan" --langs "pl,de,en"
  ```
* Generates relative **Share of Voice (SoV)** charts, tracking which diet or educational methodology is gaining market share against incumbents.

---

## Phase 2: Signal Triangulation & Commercial Intent (Mid-Term)

### 2.1. Multi-Channel Demand Triangulation
* **The "Awareness vs Intent" Challenge:** Wikipedia pageviews reflect informational curiosity, but not necessarily commercial willingness-to-pay.
* **Solution:** Integrate complementary external APIs:
  - **Google Trends API / Search Console:** Measures active commercial search queries ("buy course", "app download").
  - **App Store / Google Play Search Volume:** Correlates Wikipedia awareness spikes with app installs.
  - **Reddit / HackerNews Social Sentiment:** Detects user pain points and feature requests within target language communities.

### 2.2. News & Event Correlation Engine (GDELT)
* When a high Spike Ratio ($> 5\times$) is detected, the engine queries the **GDELT Project** or news APIs for that specific date range to automatically explain *why* the spike occurred:
  - *"Traffic spiked by 420% on 2024-11-12 due to Nobel Prize announcement in Physiology."*

---

## Phase 3: High-Scale Data Architecture & Time-Series Forecasting (Long-Term)

### 3.1. Big Data Ingestion via Wikimedia Dumps & DuckDB
* For massive batch research (e.g., screening 10,000 potential course topics across 30 languages):
  - Ingest Wikimedia hourly pageview dumps (`dumps.wikimedia.org/other/pageviews/`) using **DuckDB** or **ClickHouse**.
  - Execute vectorized SQL queries locally or in cloud object storage (S3/GCS) with sub-second latency, bypassing REST API rate limits.

### 3.2. Predictive Time-Series Forecasting
* Integrate **STL Decomposition** (Seasonal and Trend decomposition using Loess) and forecasting models (**Prophet** / **NeuralProphet**):
  - Disentangle annual seasonality (e.g., fitness topics spiking every January) from underlying structural secular trends.
  - Provide 6- to 12-month forward projections with confidence intervals for product roadmaps.

---

## Phase 4: Autonomous Product Alerts & Proactive Agent Sidecars

* **Continuous Market Watch:** Run as a scheduled agent daemon (via cron / `/schedule`):
  - Monitors high-potential emerging niches.
  - Alerts the founder via Slack / Telegram when an inflection point is detected:
    > *"🚀 Alert: 'Breathwork' in Spanish has crossed the 20% YoY organic growth threshold with high data confidence. Recommended action: test localized landing page."*
