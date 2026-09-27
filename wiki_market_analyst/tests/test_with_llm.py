"""
Script for automated end-to-end evaluation with LLMs via OpenRouter or OpenAI API.
Demonstrates how fast/budget models (Claude 3.5 Haiku, Gemini Flash, Llama 3.3)
invoke the Wiki Market Analyst tool, receive compact JSON, and formulate grounded business answers.

Usage:
    export OPENROUTER_API_KEY="sk-or-v1-..."
    python wiki_market_analyst/tests/test_with_llm.py --model "google/gemini-2.0-flash-exp:free"
    python wiki_market_analyst/tests/test_with_llm.py --model "anthropic/claude-3.5-haiku"
"""

import argparse
import json
import os
import sys
import subprocess
import requests

# Ensure UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "wiki_market_analyst",
        "description": "Analyzes Wikipedia pageviews, market demand trajectories, YoY growth, and data trust score across multiple languages. Generates charts and 1-page PDF.",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Topic to investigate (e.g. 'Astronomy', 'Intermittent fasting')"
                },
                "langs": {
                    "type": "string",
                    "description": "Comma-separated target language codes (e.g. 'uk', 'pl,cs', 'uk,pl,es,de')"
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
    topic = arguments.get("topic", "")
    langs = arguments.get("langs", "en")
    years = str(arguments.get("years", 2))
    
    script_path = os.path.join(os.path.dirname(__file__), "..", "main.py")
    cmd = [
        sys.executable,
        script_path,
        "--topic", topic,
        "--langs", langs,
        "--years", years,
        "--output-dir", "output/llm_test_run"
    ]
    
    print(f"\n[AGENT TOOL EXECUTION]: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        return json.dumps({"error": res.stderr})
    return res.stdout

def run_evaluation(model_name: str, user_question: str, api_key: str, base_url: str):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/edugenesis/84f332ba58642cf12110b196775a8b72",
        "X-Title": "Wiki Market Analyst Evaluator"
    }
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI Product Strategist evaluating market demand for B2C startup founders. "
                "Use the provided 'wiki_market_analyst' tool to inspect objective Wikipedia readership metrics "
                "before providing your recommendation. Base your conclusions strictly on growth rate, spike ratio, "
                "and the Data Trust Score."
            )
        },
        {"role": "user", "content": user_question}
    ]
    
    print(f"\n========================================================")
    print(f"Testing Model: {model_name}")
    print(f"User Prompt: {user_question}")
    print(f"========================================================")
    
    # 1. Send initial prompt with tool definition
    payload = {
        "model": model_name,
        "messages": messages,
        "tools": [TOOL_DEFINITION],
        "tool_choice": "auto"
    }
    
    response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=45)
    if response.status_code != 200:
        print(f"API Error ({response.status_code}): {response.text}")
        return

    data = response.json()
    choice = data["choices"][0]
    message = choice["message"]
    
    # 2. Check if model decided to call the tool
    tool_calls = message.get("tool_calls", [])
    if not tool_calls:
        print("\nModel responded without tool calling:")
        print(message.get("content"))
        return
        
    for tc in tool_calls:
        fn_name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])
        print(f"\n-> Model invoked tool '{fn_name}' with args: {args}")
        
        # Execute tool locally
        tool_result = execute_tool(args)
        
        # Append assistant message and tool response
        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tc["id"],
            "name": fn_name,
            "content": tool_result
        })
        
    # 3. Request final synthesis from model
    final_payload = {
        "model": model_name,
        "messages": messages
    }
    
    print("\n[AGENT REASONING & SYNTHESIS] Waiting for model response...")
    final_resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=final_payload, timeout=45)
    if final_resp.status_code == 200:
        final_answer = final_resp.json()["choices"][0]["message"]["content"]
        print("\n" + "=" * 55)
        print("FINAL GROUNDED AGENT ANSWER:")
        print("=" * 55)
        print(final_answer)
        print("=" * 55)
    else:
        print(f"Error in final response: {final_resp.text}")

def main():
    parser = argparse.ArgumentParser(description="Evaluate Wiki Market Analyst with LLMs via OpenRouter/OpenAI.")
    parser.add_argument("--model", default="google/gemini-2.0-flash-exp:free", help="Model slug on OpenRouter")
    parser.add_argument("--prompt", default="Ми думаємо додати курс з астрономії до освітнього застосунку. Чи зростає інтерес до цієї теми в україномовній Wikipedia, і наскільки цьому зростанню можна довіряти?", help="User prompt")
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1", help="API base URL")
    args = parser.parse_args()
    
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[NOTE]: OPENROUTER_API_KEY environment variable is not set.")
        print("To run live model evaluation, set your key:")
        print("    $env:OPENROUTER_API_KEY = 'sk-or-v1-...'  (PowerShell)")
        print("    export OPENROUTER_API_KEY='sk-or-v1-...'   (Linux/macOS)")
        print("\nUsing mock simulation demonstrating tool interface execution:")
        mock_output = execute_tool({"topic": "Астрономія", "langs": "uk", "years": 2})
        print("\nMock Tool Output (Structured JSON delivered to model):\n" + mock_output[:400] + "\n...[truncated]")
        return
        
    run_evaluation(args.model, args.prompt, api_key, args.base_url)

if __name__ == "__main__":
    main()
