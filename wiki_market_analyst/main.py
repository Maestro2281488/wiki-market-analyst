#!/usr/bin/env python3
"""
Single Entry Point CLI for the Wiki Market Analyst Agent Skill.

Usage:
    python main.py --topic "Intermittent fasting" --langs "pl,cs" --years 2
    python main.py --topic "Астрономія" --langs "uk" --years 2
    python main.py --topic "English language" --langs "uk,pl,es,de,cs" --years 2
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional


# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Support both direct script execution and module import
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.resolver import resolve_topic
from core.analyzer import get_date_range, fetch_pageviews_daily, analyze_traffic
from core.visualizer import generate_comparison_chart
from core.reporter import generate_pdf_report

def run_pipeline(
    topic: str,
    langs: List[str],
    years: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: str = "output",
    generate_pdf: bool = True,
    generate_chart: bool = True
) -> Dict[str, Any]:
    """
    Executes the complete market intelligence pipeline:
    1. Cross-language topic resolution (Wikidata & Wikipedia).
    2. Daily organic traffic extraction (Wikimedia API).
    3. Moving averages, YoY growth, and reliability trust scoring.
    4. Visual comparison chart generation.
    5. Single-page executive PDF report generation.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean language list
    target_langs = [l.strip().lower() for l in langs if l.strip()]
    if not target_langs:
        target_langs = ["en"]
        
    start_str, end_str, s_date, e_date = get_date_range(
        years=years,
        start_date=start_date,
        end_date=end_date
    )
    
    # Step 1: Resolve topic across languages
    resolution = resolve_topic(topic, target_langs)
    
    # Step 2: Fetch and analyze pageviews for each language
    analyses = {}
    for lang in target_langs:
        lang_res = resolution.get("languages", {}).get(lang, {})
        title = lang_res.get("title")
        exists = lang_res.get("exists", False)
        
        if exists and title:
            daily_records = fetch_pageviews_daily(lang, title, start_str, end_str)
            analysis = analyze_traffic(daily_records)
            analysis["title"] = title
            analysis["article_url"] = lang_res.get("url")
            analysis["resolution_method"] = lang_res.get("method")
            analyses[lang] = analysis
        else:
            analyses[lang] = {
                "has_data": False,
                "title": None,
                "article_url": None,
                "reason": lang_res.get("note", "Article not found"),
                "total_views": 0,
                "monthly_avg": 0,
                "growth_rate_pct": 0.0,
                "spike_ratio": 0.0,
                "volatility_cv": 0.0,
                "trust_score": 0,
                "trust_level": "NONE",
                "recommendation": "Missing Article (Market Void / Low Wikipedia Awareness)"
            }
            
    # Step 3: Visualizer
    chart_path = os.path.join(output_dir, "chart.png")
    if generate_chart:
        generate_comparison_chart(topic, analyses, output_path=chart_path)
    else:
        chart_path = None
        
    # Step 4: Reporter (PDF)
    pdf_path = os.path.join(output_dir, "report.pdf")
    date_label = f"{s_date.strftime('%Y-%m-%d')} to {e_date.strftime('%Y-%m-%d')}"
    if generate_pdf and chart_path:
        generate_pdf_report(
            topic,
            analyses,
            chart_path,
            years=years,
            date_label=date_label,
            output_pdf_path=pdf_path
        )
    else:
        pdf_path = None

    # Step 5: Synthesize executive summary bullets for the agent
    executive_bullets = []
    
    # Momentum & Volume
    data_langs = [l for l, d in analyses.items() if d.get("has_data")]
    if data_langs:
        best_growth = max(data_langs, key=lambda l: analyses[l]["growth_rate_pct"])
        best_d = analyses[best_growth]
        if best_d["growth_rate_pct"] > 0:
            executive_bullets.append(
                f"Strongest Momentum: {best_growth.upper()} shows {best_d['growth_rate_pct']:+.1f}% YoY growth "
                f"({best_d['monthly_avg']:,} views/mo, Trust: {best_d['trust_score']}%)."
            )
        else:
            executive_bullets.append(
                f"Declining / Stagnant Trend: All observed locales exhibit negative or flat growth. "
                f"Top volume in {best_growth.upper()} ({best_d['monthly_avg']:,} views/mo, {best_d['growth_rate_pct']:+.1f}% YoY)."
            )
            
        # Trust & Anomalies
        risky_langs = [l for l in data_langs if analyses[l]["trust_score"] < 50]
        if risky_langs:
            executive_bullets.append(
                f"Data Reliability Alert: High volatility or viral spikes detected in {', '.join(l.upper() for l in risky_langs)}. "
                f"Signals reflect transient media hype rather than stable recurring interest."
            )
        else:
            executive_bullets.append(
                "Data Reliability: Stable organic readership with low bot influence and no distortive spike anomalies."
            )
    else:
        executive_bullets.append(f"No active Wikipedia entries found for topic '{topic}' in requested locales.")

    # Missing locales
    missing = [l for l, d in analyses.items() if not d.get("has_data")]
    if missing:
        executive_bullets.append(
            f"Content Void: {', '.join(l.upper() for l in missing)} has no dedicated Wikipedia page. "
            f"Represents unaddressed educational demand or low top-of-funnel search awareness."
        )

    # Clean payload for agent output (remove raw date/view arrays to save tokens)
    compact_langs = {}
    for l, d in analyses.items():
        c = dict(d)
        c.pop("dates", None)
        c.pop("views", None)
        c.pop("ma_30", None)
        compact_langs[l] = c

    # Effective years duration
    days_total = (e_date - s_date).days
    effective_years = round(days_total / 365.25, 2)

    return {
        "topic": topic,
        "resolved_label": resolution.get("label"),
        "qid": resolution.get("qid"),
        "time_window_years": effective_years,
        "date_range": {
            "start": s_date.strftime("%Y-%m-%d"),
            "end": e_date.strftime("%Y-%m-%d")
        },
        "executive_summary": executive_bullets,
        "markets": compact_langs,
        "artifacts": {
            "chart_png": os.path.abspath(chart_path) if chart_path else None,
            "report_pdf": os.path.abspath(pdf_path) if pdf_path else None
        }
    }

def main():
    parser = argparse.ArgumentParser(
        description="Wiki Market Analyst: B2C market intelligence tool for AI agents."
    )
    parser.add_argument("--topic", required=True, help="Topic query string (e.g. 'Intermittent fasting', 'Астрономія')")
    parser.add_argument("--langs", default="en", help="Comma-separated language codes (e.g. 'pl,cs' or 'uk,pl,de')")
    parser.add_argument("--years", type=float, default=None, help="Number of years to analyze (e.g. 2, 4.5)")
    parser.add_argument("--start-date", default=None, help="Explicit start date (YYYY-MM-DD, e.g. 2022-02-24)")
    parser.add_argument("--end-date", default=None, help="Explicit end date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default="output", help="Directory where charts and PDFs are stored")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF generation")
    parser.add_argument("--no-chart", action="store_true", help="Skip Chart generation")
    parser.add_argument("--json", action="store_true", default=True, help="Output JSON result (default: True)")

    args = parser.parse_args()
    
    langs = [x.strip() for x in args.langs.split(",") if x.strip()]
    result = run_pipeline(
        topic=args.topic,
        langs=langs,
        years=args.years,
        start_date=args.start_date,
        end_date=args.end_date,
        output_dir=args.output_dir,
        generate_pdf=not args.no_pdf,
        generate_chart=not args.no_chart
    )

    # Print clean JSON for the AI agent
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()

