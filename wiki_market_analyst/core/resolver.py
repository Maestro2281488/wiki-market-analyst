"""
Topic and cross-language entity resolution using Wikidata and Wikipedia APIs.
Maps human query strings (in Ukrainian, English, etc.) to exact Wikipedia article titles
across multiple target language editions.
"""

from typing import Dict, List, Optional, Any
import requests
import urllib.parse

USER_AGENT = "WikiMarketAnalyst/1.0 (GenesisAISchool; https://github.com/edugenesis/84f332ba58642cf12110b196775a8b72)"

def resolve_topic(topic: str, target_langs: List[str], hint_lang: str = "en") -> Dict[str, Any]:
    """
    Resolves a search query to Wikipedia article titles across requested languages.
    
    1. Queries Wikidata wbsearchentities for the primary concept (QID).
    2. Retrieves sitelinks for requested languages (e.g. 'cswiki', 'plwiki', 'ukwiki').
    3. If a language lacks an exact sitelink, queries that language's Wikipedia directly
       to detect missing articles or closest candidates.
    """
    headers = {"User-Agent": USER_AGENT}
    resolved = {
        "query": topic,
        "qid": None,
        "label": None,
        "description": None,
        "languages": {}
    }
    
    # 1. Search Wikidata
    search_url = "https://www.wikidata.org/w/api.php"
    search_params = {
        "action": "wbsearchentities",
        "search": topic,
        "language": hint_lang,
        "limit": 5,
        "format": "json"
    }
    
    qid = None
    try:
        r = requests.get(search_url, params=search_params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            search_results = data.get("search", [])
            # If not found with hint_lang and hint_lang != 'uk', try 'uk' or 'en'
            if not search_results and hint_lang != "uk":
                search_params["language"] = "uk"
                r = requests.get(search_url, params=search_params, headers=headers, timeout=10)
                search_results = r.json().get("search", []) if r.status_code == 200 else []
            
            if search_results:
                best_match = search_results[0]
                qid = best_match.get("id")
                resolved["qid"] = qid
                resolved["label"] = best_match.get("label")
                resolved["description"] = best_match.get("description")
    except Exception as e:
        resolved["error"] = f"Wikidata search error: {str(e)}"

    sitelinks = {}
    if qid:
        try:
            entity_url = "https://www.wikidata.org/w/api.php"
            entity_params = {
                "action": "wbgetentities",
                "ids": qid,
                "props": "sitelinks",
                "format": "json"
            }
            er = requests.get(entity_url, params=entity_params, headers=headers, timeout=10)
            if er.status_code == 200:
                sitelinks = er.json().get("entities", {}).get(qid, {}).get("sitelinks", {})
        except Exception as e:
            resolved["sitelinks_error"] = str(e)
            
    # 2. Map sitelinks to target languages
    for lang in target_langs:
        wiki_key = f"{lang}wiki"
        if wiki_key in sitelinks:
            title = sitelinks[wiki_key]["title"]
            resolved["languages"][lang] = {
                "title": title,
                "exists": True,
                "method": "wikidata_sitelink",
                "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            }
        else:
            # Fallback: search target Wikipedia directly
            fallback_match = search_wiki_fallback(lang, topic, headers)
            resolved["languages"][lang] = fallback_match
            
    return resolved

def search_wiki_fallback(lang: str, query: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Fallback search directly in target language Wikipedia when Wikidata sitelink is missing.
    Distinguishes between exact article match, relevant topic candidate, and mere passing mentions.
    """
    wiki_api = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1
    }
    
    try:
        r = requests.get(wiki_api, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            hits = r.json().get("query", {}).get("search", [])
            if hits:
                top = hits[0]
                top_title = top["title"].lower()
                query_lower = query.lower()
                
                # Check for direct or close title similarity
                is_close_match = (
                    query_lower in top_title or 
                    top_title in query_lower or
                    any(word in top_title for word in query_lower.split() if len(word) > 3)
                )
                
                if is_close_match:
                    return {
                        "title": top["title"],
                        "exists": True,
                        "method": "keyword_search_fallback",
                        "note": f"Relevant match found via search: '{top['title']}'",
                        "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(top['title'].replace(' ', '_'))}"
                    }
                else:
                    return {
                        "title": None,
                        "exists": False,
                        "method": "missing_dedicated_article",
                        "note": f"No dedicated article in {lang}.wikipedia.org (only passing mentions, e.g. in '{top['title']}')",
                        "mention_context": top["title"],
                        "url": None
                    }
    except Exception as e:
        return {
            "title": None,
            "exists": False,
            "method": "error",
            "note": str(e),
            "url": None
        }
        
    return {
        "title": None,
        "exists": False,
        "method": "not_found",
        "note": f"No article found for '{query}' in {lang}.wikipedia.org",
        "url": None
    }

