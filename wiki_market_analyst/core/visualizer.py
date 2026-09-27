"""
Visualizer module for Wiki Market Analyst.
Generates clean, presentation-ready charts comparing pageview trajectories,
30-day smoothed moving averages, and growth dynamics across language editions.
"""

from typing import Dict, Any, List
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

PALETTE = [
    "#2563EB",  # Blue
    "#10B981",  # Emerald Green
    "#F59E0B",  # Amber
    "#EC4899",  # Pink
    "#8B5CF6",  # Purple
    "#06B6D4",  # Cyan
    "#EF4444",  # Red
]

def generate_comparison_chart(
    topic: str,
    analyses: Dict[str, Dict[str, Any]],
    output_path: str = "output/chart.png"
) -> str:
    """
    Renders a multi-panel market intelligence chart:
    - Panel 1 (Top): 30-Day Moving Average trendlines comparing language sections over time.
    - Panel 2 (Bottom Left): YoY Growth % comparison bar chart.
    - Panel 3 (Bottom Right): Data Trust Score & Volume gauge/bars.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # Filter languages with valid data
    active_langs = [l for l, d in analyses.items() if d.get("has_data") and d.get("dates")]
    
    fig = plt.figure(figsize=(12, 8), dpi=180)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.6, 1.0], hspace=0.35, wspace=0.25)
    
    # --- Panel 1: Trend Over Time ---
    ax_trend = fig.add_subplot(gs[0, :])
    
    if not active_langs:
        ax_trend.text(0.5, 0.5, f"No pageview data found for '{topic}' in requested languages",
                      ha="center", va="center", fontsize=14, color="#64748B")
        ax_trend.set_axis_off()
    else:
        for idx, lang in enumerate(active_langs):
            d = analyses[lang]
            dates = [datetime.strptime(x, "%Y-%m-%d") for x in d["dates"]]
            ma_30 = d["ma_30"]
            color = PALETTE[idx % len(PALETTE)]
            label = f"{lang.upper()} ({d.get('title', lang)}): {d['growth_rate_pct']:+.1f}% YoY"
            
            # Plot daily points faintly
            ax_trend.plot(dates, d["views"], color=color, alpha=0.15, linewidth=0.8)
            # Plot smoothed 30-day moving average prominently
            ax_trend.plot(dates, ma_30, color=color, linewidth=2.4, label=label)
            
        ax_trend.set_title(f"Wikimedia Demand Dynamics: '{topic}' (30-day Smoothed Trend)",
                           fontsize=14, fontweight="bold", pad=12, color="#0F172A")
        ax_trend.set_ylabel("Daily Human Views (MA 30)", fontsize=11, color="#334155")
        
        # Adaptive date locator to prevent overlapping date labels
        date_locator = mdates.AutoDateLocator(minticks=5, maxticks=9)
        ax_trend.xaxis.set_major_locator(date_locator)
        ax_trend.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(ax_trend.get_xticklabels(), rotation=25, ha="right", fontsize=9)
        
        ax_trend.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
        ax_trend.legend(frameon=True, facecolor="#F8FAFC", edgecolor="#E2E8F0", fontsize=10, loc="upper left")
        ax_trend.tick_params(colors="#475569")

    # --- Panel 2: YoY Growth Rate Comparison ---
    ax_growth = fig.add_subplot(gs[1, 0])
    all_langs = list(analyses.keys())
    growth_vals = []
    labels = []
    bar_colors = []
    
    for l in all_langs:
        d = analyses[l]
        labels.append(l.upper())
        if d.get("has_data"):
            g = d["growth_rate_pct"]
            growth_vals.append(g)
            bar_colors.append("#10B981" if g >= 0 else "#EF4444")
        else:
            growth_vals.append(0.0)
            bar_colors.append("#94A3B8")
            
    bars = ax_growth.bar(labels, growth_vals, color=bar_colors, width=0.45, edgecolor="#0F172A", linewidth=0.5)
    ax_growth.axhline(0, color="#64748B", linewidth=1.0)
    ax_growth.set_title("Period Growth Rate (% YoY)", fontsize=12, fontweight="bold", color="#0F172A")
    ax_growth.set_ylabel("Growth %", fontsize=10, color="#334155")
    ax_growth.grid(True, axis="y", linestyle="--", alpha=0.4, color="#CBD5E1")
    ax_growth.tick_params(colors="#475569")
    
    # Calculate adaptive headroom so labels never clip outside the subplot
    min_g = min(growth_vals) if growth_vals else 0.0
    max_g = max(growth_vals) if growth_vals else 0.0
    pad_top = max(abs(max_g) * 0.25, 20.0)
    pad_bot = max(abs(min_g) * 0.25, 20.0) if min_g < 0 else 5.0
    ax_growth.set_ylim(min_g - pad_bot, max_g + pad_top)
    
    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        # Format percentage nicely (handle large numbers like +18k%)
        if abs(h) >= 10000:
            pct_text = f"{h/1000:+.1f}k%"
        elif abs(h) >= 1000:
            pct_text = f"{h:+,.0f}%"
        else:
            pct_text = f"{h:+.1f}%"
            
        y_pos = h + (pad_top * 0.05 if h >= 0 else -pad_bot * 0.05)
        ax_growth.text(
            bar.get_x() + bar.get_width() / 2,
            y_pos,
            pct_text,
            ha="center",
            va=va,
            fontsize=9,
            fontweight="bold",
            color="#0F172A"
        )

    # --- Panel 3: Data Reliability / Trust Score ---
    ax_trust = fig.add_subplot(gs[1, 1])
    trust_scores = []
    trust_colors = []
    for l in all_langs:
        d = analyses[l]
        if d.get("has_data"):
            score = d["trust_score"]
            trust_scores.append(score)
            if score >= 75:
                trust_colors.append("#10B981")
            elif score >= 50:
                trust_colors.append("#F59E0B")
            else:
                trust_colors.append("#EF4444")
        else:
            trust_scores.append(0)
            trust_colors.append("#CBD5E1")
            
    bars_t = ax_trust.bar(labels, trust_scores, color=trust_colors, width=0.45, edgecolor="#0F172A", linewidth=0.5)
    # Headroom up to 125 so 100% text never touches the top border
    ax_trust.set_ylim(0, 125)
    ax_trust.set_title("Data Trust Score (0-100%)", fontsize=12, fontweight="bold", color="#0F172A")
    ax_trust.set_ylabel("Confidence %", fontsize=10, color="#334155")
    ax_trust.grid(True, axis="y", linestyle="--", alpha=0.4, color="#CBD5E1")
    ax_trust.tick_params(colors="#475569")
    
    for bar in bars_t:
        h = bar.get_height()
        ax_trust.text(
            bar.get_x() + bar.get_width() / 2,
            h + 3,
            f"{int(h)}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#0F172A"
        )

    plt.savefig(output_path, bbox_inches="tight", dpi=180)
    plt.close(fig)
    return output_path

