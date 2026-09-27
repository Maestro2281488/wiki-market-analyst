"""
Automated end-to-end evaluation script specifically for Google Gemini models.
Uses Gemini's OpenAI-compatible endpoint (no extra SDK installation required, works with 'requests').

Usage:
    # 1. Set your Gemini API key in PowerShell:
    $env:GEMINI_API_KEY = "AIzaSy..."

    # 2. Run test with Gemini 2.0 Flash:
    python wiki_market_analyst/tests/test_with_gemini.py

    # Or specify custom prompt and model:
    python wiki_market_analyst/tests/test_with_gemini.py --model "gemini-2.0-flash" --prompt "Порівняй інтерес до інтервального голодування в Польщі та Чехії за 2 роки."
"""

import argparse
import json
import os
import sys
import subprocess
import requests

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GEMINI_OPENAI_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "wiki_market_analyst",
        "description": "Analyzes Wikipedia pageviews, market demand trajectories, YoY growth, and data trust score across multiple languages (e.g. 'ua', 'pl', 'cs', 'en'). Generates comparison charts and a 1-page PDF report.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The topic or concept to investigate (e.g. 'Астрономія', 'Intermittent fasting')"
                },
                "langs": {
                    "type": "string",
                    "description": "Comma-separated target language codes (e.g. 'ua', 'pl,cs', 'ua,pl,es,de,cs')"
                },
                "years": {
                    "type": "number",
                    "description": "Observation window in years (default 2)"
                }
            },
            "required": ["topic", "langs"]
        }
    }
}

def execute_tool(arguments: dict) -> str:
    """Executes main.py as a subprocess and captures JSON output."""
    topic = str(arguments.get("topic", ""))
    langs = str(arguments.get("langs", "ua"))
    years = str(arguments.get("years", 2))
    
    script_path = os.path.join(os.path.dirname(__file__), "..", "main.py")
    cmd = [
        sys.executable,
        script_path,
        "--topic", topic,
        "--langs", langs,
        "--years", years,
        "--output-dir", "output/gemini_test_run"
    ]
    
    print(f"\n[AI AGENT TOOL EXECUTION]: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return json.dumps({"error": res.stderr})
    return res.stdout

def run_gemini_test(api_key: str, model_name: str, user_prompt: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are an expert AI Product Strategist advising B2C startup founders. "
        "A founder has asked you a business question about market interest. "
        "You MUST first use the 'wiki_market_analyst' tool to inspect objective Wikipedia metrics "
        "before answering. Base your final recommendation strictly on growth rate, spike ratio, "
        "and the Data Trust Score provided in the tool output."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    print("=" * 65)
    print(f"Testing Model: Google {model_name}")
    print(f"Founder Question: {user_prompt}")
    print("=" * 65)
    
    # 1. Send initial prompt with tool definition
    payload = {
        "model": model_name,
        "messages": messages,
        "tools": [TOOL_DEFINITION],
        "tool_choice": "auto"
    }
    
    print(f"\n[1/3] Sending request to Gemini with tool definitions...")
    try:
        response = requests.post(GEMINI_OPENAI_URL, headers=headers, json=payload, timeout=60)
    except Exception as e:
        print(f"Network error connecting to Gemini API: {e}")
        return

    if response.status_code != 200:
        print(f"Gemini API Error (Status {response.status_code}):\n{response.text}")
        return

    resp_json = response.json()
    choice = resp_json["choices"][0]
    message = choice["message"]
    
    # 2. Check if Gemini decided to invoke the tool
    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        print("\nGemini answered without calling the tool:")
        print(message.get("content"))
        return
        
    print(f"\n[2/3] Gemini successfully decided to call the tool!")
    messages.append(message)
    
    for tc in tool_calls:
        fn_name = tc["function"]["name"]
        raw_args = tc["function"]["arguments"]
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        print(f"-> Function Name: {fn_name}")
        print(f"-> Arguments: {json.dumps(args, ensure_ascii=False)}")
        
        # Execute tool locally via main.py
        tool_output_str = execute_tool(args)
        
        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "name": fn_name,
            "content": tool_output_str
        })
        
    # 3. Request final business recommendation from Gemini
    print("\n[3/3] Feeding tool JSON output back to Gemini for final synthesis...")
    final_payload = {
        "model": model_name,
        "messages": messages
    }
    
    final_resp = requests.post(GEMINI_OPENAI_URL, headers=headers, json=final_payload, timeout=60)
    if final_resp.status_code == 200:
        final_answer = final_resp.json()["choices"][0]["message"]["content"]
        print("\n" + "=" * 65)
        print("🎯 FINAL GEMINI PRODUCT RECOMMENDATION:")
        print("=" * 65)
        print(final_answer)
        print("=" * 65)
        print("\nArtifacts saved in: output/gemini_test_run/ (chart.png and report.pdf)")
    else:
        print(f"Error getting final Gemini response:\n{final_resp.text}")

def main():
    parser = argparse.ArgumentParser(description="Test Wiki Market Analyst skill with Google Gemini API.")
    parser.add_argument("--api-key", default=None, help="Your Gemini API key (or set GEMINI_API_KEY env variable)")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Gemini model name (e.g. 'gemini-2.0-flash', 'gemini-1.5-flash')")
    parser.add_argument(
        "--prompt",
        default="Ми думаємо додати курс з астрономії до освітнього застосунку. Чи зростає інтерес до цієї теми в україномовній Wikipedia, і наскільки цьому зростанню можна довіряти?",
        help="Question to ask the model"
    )
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n[УВАГА] Не знайдено API ключ Gemini!")
        print("Будь ласка, встановіть його через змінну середовища:")
        print("    $env:GEMINI_API_KEY = \"AIzaSy...\"   (у PowerShell)")
        print("Або передайте прапорцем:")
        print("    python wiki_market_analyst/tests/test_with_gemini.py --api-key \"AIzaSy...\"")
        sys.exit(1)
        
    run_gemini_test(api_key, args.model, args.prompt)

if __name__ == "__main__":
    main()
