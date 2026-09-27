"""
Analyzer module for Wikipedia Pageviews.
Fetches organic user traffic, calculates smoothed trends (moving averages),
computes growth rates (YoY), anomaly/spike indices, and business trust scores.
"""

from typing import Dict, List, Optional, Any, Tuple
import datetime
import json
import os
import urllib.parse
import numpy as np
import requests

USER_AGENT = "WikiMarketAnalyst/1.0 (GenesisAISchool; https://github.com/edugenesis/84f332ba58642cf12110b196775a8b72)"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", ".cache")

def get_date_range(
    years: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[str, str, datetime.date, datetime.date]:
    """
    Computes start and end timestamps in Wikimedia format (YYYYMMDD00).
    Supports either explicit start/end dates (YYYY-MM-DD or YYYYMMDD) or a relative 'years' duration.
    """
    today = datetime.date.today()
    default_end = today - datetime.timedelta(days=2)
    
    if end_date:
        clean_end = end_date.replace("-", "").strip()
        e_date = datetime.datetime.strptime(clean_end, "%Y%m%d").date()
    else:
        e_date = default_end

    if start_date:
        clean_start = start_date.replace("-", "").strip()
        s_date = datetime.datetime.strptime(clean_start, "%Y%m%d").date()
    else:
        num_years = years if years is not None else 2.0
        s_date = e_date - datetime.timedelta(days=int(num_years * 365.25))

    start_str = s_date.strftime("%Y%m%d00")
    end_str = e_date.strftime("%Y%m%d00")
    return start_str, end_str, s_date, e_date


def fetch_redirects(lang: str, article_title: str) -> List[str]:
    """Retrieves top redirects pointing to this article in the given language wiki."""
    wiki_api = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": article_title,
        "prop": "redirects",
        "rdlimit": "max",
        "format": "json"
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        r = requests.get(wiki_api, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            pages = r.json().get("query", {}).get("pages", {})
            for pid, p in pages.items():
                reds = [red["title"] for red in p.get("redirects", [])]
                # Prioritize canonical case variations and common redirects
                return reds
    except Exception:
        pass
    return []

def fetch_pageviews_daily(
    lang: str,
    article_title: str,
    start_str: str,
    end_str: str,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Fetches daily pageviews from Wikimedia API filtered to human users ('agent=user').
    Automatically merges views from primary redirects if a page was moved/renamed.
    Uses local cache to prevent redundant network calls during iterative queries.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_title = urllib.parse.quote(article_title.replace(" ", "_"), safe="")
    cache_filename = f"{lang}_{safe_title}_{start_str}_{end_str}_v3.json"
    cache_path = os.path.join(CACHE_DIR, cache_filename)
    
    if use_cache and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    project = f"{lang}.wikipedia.org"
    url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/user/{safe_title}/daily/{start_str}/{end_str}"
    headers = {"User-Agent": USER_AGENT}
    
    daily_map = {}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            for it in r.json().get("items", []):
                daily_map[it["timestamp"][:8]] = it["views"]
    except Exception:
        pass

    # Check top redirects if page was renamed/moved (e.g. Russian invasion of Ukraine -> Russo-Ukrainian war)
    redirects = fetch_redirects(lang, article_title)
    candidates = []
    lower_title = article_title.lower()
    stems = [w[:4] for w in lower_title.replace("-", " ").replace("(", " ").replace(")", " ").split() if len(w) >= 4]
    for red in redirects:
        r_low = red.lower()
        if any(s in r_low for s in stems):
            candidates.append(red)
            
    def cand_priority(c: str) -> float:
        c_low = c.lower()
        score = 0.0
        if "russian invasion of ukraine" in c_low:
            score += 100.0
        if "invasion" in c_low or "war" in c_low or "вторгнення" in c_low or "війна" in c_low:
            score += 10.0
        score -= len(c) * 0.05
        return score

    candidates.sort(key=cand_priority, reverse=True)

    # Probe top candidates
    for red in candidates[:15]:
        safe_red = urllib.parse.quote(red.replace(" ", "_"), safe="")
        red_url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/user/{safe_red}/daily/{start_str}/{end_str}"
        try:
            rr = requests.get(red_url, headers=headers, timeout=10)
            if rr.status_code == 200:
                items = rr.json().get("items", [])
                if sum(x["views"] for x in items) > 500:
                    for it in items:
                        dt = it["timestamp"][:8]
                        daily_map[dt] = daily_map.get(dt, 0) + it["views"]
        except Exception:
            pass

    if daily_map:
        sorted_dates = sorted(daily_map.keys())
        data = [{"date": dt, "views": daily_map[dt]} for dt in sorted_dates]
        if use_cache:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        return data

        
    return []


        
    return []

def calculate_moving_average(values: List[float], window: int = 30) -> List[float]:
    """Computes rolling moving average with border reflection."""
    if not values:
        return []
    if len(values) < window:
        window = max(1, len(values) // 2)
    weights = np.ones(window) / window
    # Valid convolution padded with edge values
    padded = np.pad(values, (window // 2, window - 1 - window // 2), mode="edge")
    ma = np.convolve(padded, weights, mode="valid")
    return [round(float(x), 2) for x in ma]

def analyze_traffic(daily_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates statistical and product metrics from raw daily pageview records:
    - Total Volume & Monthly Average
    - 30-day Moving Average trend
    - Period-over-Period (YoY) Growth %
    - Volatility (Coefficient of Variation)
    - Spike Ratio (anomaly peak detection)
    - Trust / Confidence Score (0-100%)
    - Strategic Actionable Recommendation Tag
    """
    if not daily_data:
        return {
            "has_data": False,
            "total_views": 0,
            "daily_avg": 0,
            "monthly_avg": 0,
            "growth_rate_pct": 0.0,
            "volatility_cv": 0.0,
            "spike_ratio": 0.0,
            "trust_score": 0,
            "trust_level": "NONE",
            "recommendation": "Missing Data / Inactive Topic",
            "daily_series": [],
            "ma_30": []
        }

    views = [d["views"] for d in daily_data]
    dates = [f"{d['date'][:4]}-{d['date'][4:6]}-{d['date'][6:]}" for d in daily_data]
    n_days = len(views)
    total_views = int(sum(views))
    daily_avg = float(np.mean(views))
    monthly_avg = daily_avg * 30.4375
    std_dev = float(np.std(views))
    max_views = int(np.max(views))

    # 1. Moving Averages
    ma_30 = calculate_moving_average(views, window=30)

    # 2. Period-over-Period (YoY) Growth
    # Split observations into first half and second half
    mid_point = n_days // 2
    period1 = views[:mid_point]
    period2 = views[mid_point:]
    sum_p1 = sum(period1)
    sum_p2 = sum(period2)
    
    if sum_p1 > 0:
        growth_rate_pct = round(((sum_p2 - sum_p1) / sum_p1) * 100.0, 1)
    else:
        growth_rate_pct = 0.0

    # 3. Volatility and Spike Ratio
    volatility_cv = round(std_dev / daily_avg, 2) if daily_avg > 0 else 0.0
    spike_ratio = round(max_views / daily_avg, 1) if daily_avg > 0 else 0.0

    # Top 5% peak days concentration
    k_top = max(1, int(n_days * 0.05))
    top_5_pct_views = sum(sorted(views, reverse=True)[:k_top])
    concentration_ratio = round(top_5_pct_views / total_views, 2) if total_views > 0 else 0.0

    # 4. Data Trust / Reliability Score (0-100)
    trust_score = 100
    penalties = []

    # Sample size penalty
    annual_estimate = total_views * (365.0 / n_days) if n_days > 0 else 0
    if annual_estimate < 1500:
        trust_score -= 40
        penalties.append("Very low search volume (< 1.5k/year)")
    elif annual_estimate < 5000:
        trust_score -= 20
        penalties.append("Modest search volume (< 5k/year)")

    # Spike / Anomaly dominance penalty
    if spike_ratio > 10.0:
        trust_score -= 25
        penalties.append(f"Extreme single-day spike ({spike_ratio}x of average)")
    elif spike_ratio > 5.0:
        trust_score -= 15
        penalties.append(f"Elevated peak spike ({spike_ratio}x of average)")

    # Extreme concentration penalty (e.g. news viral hit)
    if concentration_ratio > 0.35:
        trust_score -= 20
        penalties.append("Top 5% days dominate >35% of total volume (event-driven)")

    # Volatility penalty
    if volatility_cv > 1.2:
        trust_score -= 15
        penalties.append("High traffic volatility (unstable daily demand)")

    trust_score = max(5, min(100, trust_score))

    if trust_score >= 75:
        trust_level = "HIGH"
    elif trust_score >= 50:
        trust_level = "MODERATE"
    else:
        trust_level = "LOW"

    # 5. Product Recommendation Heuristic
    if annual_estimate < 1500:
        recommendation = "Low Awareness / Niche"
    elif growth_rate_pct >= 20.0 and trust_level == "HIGH":
        recommendation = "Greenfield Opportunity (Strong Organic Growth)"
    elif growth_rate_pct >= 15.0 and trust_level in ("HIGH", "MODERATE"):
        recommendation = "Growing Interest (Viable Expansion Target)"
    elif spike_ratio > 6.0 and trust_level == "LOW":
        recommendation = "Hype-Driven / High Anomaly Risk"
    elif growth_rate_pct <= -15.0 and trust_level != "LOW":
        recommendation = "Declining Interest (Caution / Deprioritize)"
    elif -10.0 <= growth_rate_pct <= 15.0 and annual_estimate >= 5000:
        recommendation = "Stable Baseline Demand (Low Growth, Evergreen)"
    else:
        recommendation = "Moderate Interest (Requires Product-Led Validation)"

    return {
        "has_data": True,
        "n_days": n_days,
        "total_views": total_views,
        "daily_avg": round(daily_avg, 1),
        "monthly_avg": int(round(monthly_avg)),
        "growth_rate_pct": growth_rate_pct,
        "volatility_cv": volatility_cv,
        "spike_ratio": spike_ratio,
        "concentration_top5_pct": concentration_ratio,
        "trust_score": trust_score,
        "trust_level": trust_level,
        "penalties": penalties,
        "recommendation": recommendation,
        "dates": dates,
        "views": views,
        "ma_30": ma_30
    }
