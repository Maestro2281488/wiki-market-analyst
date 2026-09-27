"""
Reporter module for Wiki Market Analyst.
Generates an executive, single-page PDF report using fpdf2,
tailored for B2C product founders, PMs, and leadership teams.
"""

from typing import Dict, Any, List, Optional
import os
import datetime
from fpdf import FPDF

def find_unicode_font() -> Dict[str, Optional[str]]:
    """Locates suitable Unicode TrueType fonts on the host system."""
    candidates = [
        # Windows
        {"reg": "C:/Windows/Fonts/arial.ttf", "bold": "C:/Windows/Fonts/arialbd.ttf"},
        {"reg": "C:/Windows/Fonts/segoeui.ttf", "bold": "C:/Windows/Fonts/segoeuib.ttf"},
        # Linux
        {"reg": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"},
        {"reg": "/usr/share/fonts/truetype/freefont/FreeSans.ttf", "bold": "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"},
        # MacOS
        {"reg": "/System/Library/Fonts/Supplemental/Arial.ttf", "bold": "/System/Library/Fonts/Supplemental/Arial Bold.ttf"}
    ]
    for c in candidates:
        if os.path.exists(c["reg"]):
            bold_path = c["bold"] if os.path.exists(c["bold"]) else None
            return {"reg": c["reg"], "bold": bold_path}
    return {"reg": None, "bold": None}

class ExecutiveReportPDF(FPDF):
    def __init__(self, font_info: Dict[str, Optional[str]]):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(12, 10, 12)
        self.set_auto_page_break(auto=False)
        self.font_info = font_info
        
        if font_info["reg"]:
            self.add_font("CustomSans", "", font_info["reg"])
            if font_info["bold"]:
                self.add_font("CustomSans", "B", font_info["bold"])
            else:
                self.add_font("CustomSans", "B", font_info["reg"])
            self.font_family_name = "CustomSans"
        else:
            self.font_family_name = "Helvetica"

    def header(self):
        # We manually render the executive banner in generate_pdf
        pass

    def footer(self):
        self.set_y(-10)
        self.set_font(self.font_family_name, "", 7)
        self.set_text_color(148, 163, 184)
        self.cell(0, 5, "Wiki Market Analyst · Author: Mykola Shuprovych · Genesis AI School · Confidential & Strategic", align="C")

def generate_pdf_report(
    topic: str,
    analyses: Dict[str, Dict[str, Any]],
    chart_path: str,
    years: Optional[float] = None,
    date_label: Optional[str] = None,
    output_pdf_path: str = "output/report.pdf"
) -> str:
    """
    Renders an executive 1-page PDF summarizing Wikimedia audience signals.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    font_info = find_unicode_font()
    pdf = ExecutiveReportPDF(font_info)
    font_name = pdf.font_family_name
    pdf.add_page()

    # --- 1. HEADER BANNER ---
    pdf.set_fill_color(15, 23, 42)  # #0F172A slate-900
    pdf.rect(12, 10, 186, 22, "F")
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(font_name, "B", 14)
    pdf.set_xy(16, 12)
    # Sanitize title for standard font if unicode missing
    display_topic = topic if font_info["reg"] else topic.encode("ascii", "replace").decode()
    pdf.cell(110, 8, f"Wikimedia Market Demand: {display_topic}")
    
    pdf.set_font(font_name, "", 8)
    pdf.set_xy(16, 20)
    pdf.set_text_color(203, 213, 225)
    pdf.cell(110, 6, "Audience Trajectory, Reliability Scoring & Business Expansion Evaluation")
    
    # Header metadata box (Right)
    pdf.set_xy(135, 12)
    pdf.set_font(font_name, "B", 7)
    window_str = date_label if date_label else f"Window: {years or 2} Years"
    pdf.cell(58, 4, window_str, align="R")
    pdf.set_xy(135, 16)
    pdf.set_font(font_name, "", 7)
    pdf.cell(58, 4, f"Generated: {datetime.date.today().strftime('%Y-%m-%d')}", align="R")

def get_display_code(lang: str) -> str:
    """Returns business-standard display code (e.g. UA instead of UK to avoid United Kingdom confusion)."""
    l_low = lang.lower().strip()
    if l_low in ("uk", "ua", "ukr"):
        return "UA"
    return l_low.upper()

    pdf.set_xy(135, 20)
    pdf.cell(58, 4, f"Languages: {', '.join(get_display_code(l) for l in analyses.keys())}", align="R")

    # --- 2. EXECUTIVE SUMMARY BULLETS ---
    pdf.set_y(35)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font(font_name, "B", 10)
    pdf.cell(0, 5, "Executive Findings & Product Actionability:")
    pdf.ln(6)

    # Compute key executive insights
    best_lang = None
    best_growth = -999.0
    highest_vol_lang = None
    highest_vol = 0
    missing_langs = []

    for l, d in analyses.items():
        if d.get("has_data"):
            if d["total_views"] > highest_vol:
                highest_vol = d["total_views"]
                highest_vol_lang = l
            if d["growth_rate_pct"] > best_growth and d["trust_score"] >= 50:
                best_growth = d["growth_rate_pct"]
                best_lang = l
        else:
            missing_langs.append(l)

    pdf.set_font(font_name, "", 8)
    pdf.set_text_color(51, 65, 85)
    
    # Bullet 1: Growth & Primary Target
    if best_lang:
        b1 = f"• Primary Momentum: '{get_display_code(best_lang)}' exhibits the strongest trend (+{best_growth:.1f}% YoY) with {analyses[best_lang]['trust_level']} data confidence."
    elif highest_vol_lang:
        b1 = f"• Demand Volume: '{get_display_code(highest_vol_lang)}' leads total organic traffic ({analyses[highest_vol_lang]['monthly_avg']:,} views/mo), but growth is flat or negative."
    else:
        b1 = "• Traffic Signals: Low or declining search interest observed across analyzed language segments."
    pdf.cell(0, 4, b1)
    pdf.ln(4.5)

    # Bullet 2: Trust & Risk
    low_trust = [l for l, d in analyses.items() if d.get("has_data") and d["trust_score"] < 50]
    if low_trust:
        b2 = f"• Reliability Caveat: {', '.join(get_display_code(l) for l in low_trust)} shows elevated volatility or single-day spikes. Treat as PR/media hype rather than steady search intent."
    else:
        b2 = "• Signal Quality: Observed traffic shows high stability without distortive bot spikes or transient viral hype."
    pdf.cell(0, 4, b2)
    pdf.ln(4.5)

    # Bullet 3: Content Void / Localization
    if missing_langs:
        b3 = f"• Opportunity / Gap: {', '.join(get_display_code(l) for l in missing_langs)} lacks dedicated Wikipedia coverage. High potential for brand-led content or indicates lower organic awareness."
    else:
        b3 = "• Coverage: Dedicated Wikipedia articles exist across all requested locales, confirming active informational baselines."

    pdf.cell(0, 4, b3)
    pdf.ln(6)

    # --- 3. METRICS TABLE ---
    # Columns: Language (18) | Article Title (50) | Monthly Avg (25) | Growth YoY (25) | Volatility/Spike (28) | Trust Score (20) | Strategic Tag (20)
    col_w = [14, 52, 22, 22, 24, 22, 30]
    
    # Table Header
    pdf.set_fill_color(241, 245, 249)  # #F1F5F9
    pdf.set_text_color(71, 85, 105)
    pdf.set_font(font_name, "B", 7.5)
    
    pdf.cell(col_w[0], 6, "Lang", border=1, fill=True, align="C")
    pdf.cell(col_w[1], 6, "Wikipedia Article", border=1, fill=True, align="L")
    pdf.cell(col_w[2], 6, "Monthly Views", border=1, fill=True, align="R")
    pdf.cell(col_w[3], 6, "Growth YoY", border=1, fill=True, align="R")
    pdf.cell(col_w[4], 6, "Spike Ratio", border=1, fill=True, align="R")
    pdf.cell(col_w[5], 6, "Trust Score", border=1, fill=True, align="C")
    pdf.cell(col_w[6], 6, "Strategic Signal", border=1, fill=True, align="L")
    pdf.ln(6)

    pdf.set_font(font_name, "", 7.5)
    pdf.set_text_color(15, 23, 42)

    for lang, d in analyses.items():
        if d.get("has_data"):
            title = d.get("title", "—")
            if len(title) > 30:
                title = title[:28] + ".."
            m_views = f"{d['monthly_avg']:,}"
            growth = f"{d['growth_rate_pct']:+.1f}%"
            spike = f"{d['spike_ratio']}x"
            trust = f"{d['trust_score']}% ({d['trust_level']})"
            rec = d.get("recommendation", "—")
            if len(rec) > 18:
                rec = rec.split("(")[0].strip()
        else:
            title = "Missing Article"
            m_views = "0"
            growth = "N/A"
            spike = "N/A"
            trust = "0% (NONE)"
            rec = "No Article / Void"

        pdf.cell(col_w[0], 5.5, get_display_code(lang), border=1, align="C")
        pdf.cell(col_w[1], 5.5, title, border=1, align="L")
        pdf.cell(col_w[2], 5.5, m_views, border=1, align="R")
        pdf.cell(col_w[3], 5.5, growth, border=1, align="R")
        pdf.cell(col_w[4], 5.5, spike, border=1, align="R")
        pdf.cell(col_w[5], 5.5, trust, border=1, align="C")
        pdf.cell(col_w[6], 5.5, rec[:22], border=1, align="L")
        pdf.ln(5.5)

    pdf.ln(3)

    # --- 4. EMBEDDED CHART ---
    if os.path.exists(chart_path):
        # Render chart in center (width ~ 186mm)
        chart_y = pdf.get_y()
        pdf.image(chart_path, x=12, y=chart_y, w=186, h=108)
        pdf.set_y(chart_y + 110)

    # --- 5. ASSUMPTIONS & RISKS FOOTER ---
    pdf.set_fill_color(248, 250, 252)
    pdf.rect(12, pdf.get_y(), 186, 20, "F")
    
    pdf.set_xy(14, pdf.get_y() + 1.5)
    pdf.set_font(font_name, "B", 7.5)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 4, "Methodological Assumptions & Limitations for Founders:")
    pdf.ln(4)
    
    pdf.set_font(font_name, "", 6.8)
    pdf.set_text_color(100, 116, 139)
    assumptions_text = (
        "1. Traffic Filter: Wikimedia API queries human users ('agent=user'), excluding automated scrapers.\n"
        "2. Awareness != Intent: Wikipedia readership measures informational interest, not direct commercial willingness-to-pay.\n"
        "3. Spikes vs Baseline: Sharp spikes usually reflect one-off media events; sustainable B2C courses require 30-day baseline growth."
    )
    pdf.multi_cell(182, 3.2, assumptions_text)

    pdf.output(output_pdf_path)
    return output_pdf_path
