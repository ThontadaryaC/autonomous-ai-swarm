import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse
import re
import random
import threading
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests
import ollama

import skill_evolver

# Learning curriculum topics for continuous skill acquisition
RESEARCH_TOPICS = [
    {"skill": "cybersecurity", "query": "OWASP top 10 web application vulnerabilities and prevention code patterns"},
    {"skill": "cybersecurity", "query": "Python secure coding practices preventing SQL injection and XSS"},
    {"skill": "backend_coding", "query": "Modern Python FastAPI best practices scalable architecture"},
    {"skill": "backend_coding", "query": "High performance clean code design patterns backend API"},
    {"skill": "frontend_ui", "query": "Modern responsive CSS glassmorphism and animated UI components design"},
    {"skill": "frontend_ui", "query": "Accessible interactive JavaScript DOM best practices 2026"},
    {"skill": "qa_testing", "query": "Automated unit testing with PyTest mocking integration strategies"},
    {"skill": "qa_testing", "query": "Software quality assurance automated regression testing pipeline"}
]

LEARNING_LOG_FILE = "c:/Users/cool/Desktop/skills/autonomous_learning_log.json"

def is_connected_to_internet() -> bool:
    """Checks if active internet connection is available."""
    try:
        urllib.request.urlopen("https://1.1.1.1", timeout=4)
        return True
    except Exception:
        try:
            urllib.request.urlopen("https://www.google.com", timeout=4)
            return True
        except Exception:
            return False

def search_web_for_topic(query: str) -> list:
    """Searches DuckDuckGo for top learning articles."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        encoded = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
        
        snippets = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        clean_snippets = [re.sub(r'<.*?>', '', s).strip() for s in snippets[:4]]
        return clean_snippets
    except Exception as e:
        return [f"Search error: {str(e)}"]

def learn_from_topic(topic_item: dict, model: str = "qwen3:4b") -> dict:
    """Performs one learning session: searches web, synthesizes lessons, and evolves skills."""
    skill_name = topic_item["skill"]
    query = topic_item["query"]
    today_str = datetime.date.today().isoformat()
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    print(f"\n🌐 [{now_str}] Autonomous Web Learner researching: '{query}' ({skill_name})")
    snippets = search_web_for_topic(query)
    combined_knowledge = "\n".join(snippets)

    synthesis_prompt = f"""You are the AI Autonomous Continuous Learner.
You just retrieved latest technical data from the web regarding: "{query}"

WEB KNOWLEDGE:
{combined_knowledge}

Extract 1 high-value, practical technical lesson/rule for the skill '{skill_name}'.
Return ONLY valid JSON in this exact structure:
{{
  "title": "Short title of learned insight",
  "rule": "Detailed actionable coding or security rule to apply in future projects",
  "category": "{skill_name}"
}}
"""

    host = os.environ.get("OLLAMA_HOST", "https://catalogue-president-eyes-fairy.trycloudflare.com")
    client = ollama.Client(host=host)

    try:
        resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": synthesis_prompt}],
            format="json"
        )
        data = json.loads(resp.message.content)
    except Exception:
        # Fallback synthesis if offline or remote fails
        data = {
            "title": f"Applied insights from {query[:40]}",
            "rule": f"Integrate standard defensive patterns and modular code for {skill_name}.",
            "category": skill_name
        }

    # Save to persistent skills memory
    mem = skill_evolver.load_memory()
    if skill_name in mem["skills"]:
        mem["skills"][skill_name]["learnings"].append({
            "date": today_str,
            "time": now_str,
            "source": "autonomous_web_learning",
            "summary": data.get("title"),
            "rule": data.get("rule")
        })
        mem["skills"][skill_name]["level"] = 1 + (len(mem["skills"][skill_name]["learnings"]) // 2)
    skill_evolver.save_memory(mem)

    # Save to Autonomous Learning Log
    logs = []
    if os.path.exists(LEARNING_LOG_FILE):
        try:
            with open(LEARNING_LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception:
            logs = []

    learning_record = {
        "timestamp": f"{today_str} {now_str}",
        "topic": query,
        "skill": skill_name,
        "title": data.get("title"),
        "rule": data.get("rule")
    }
    logs.append(learning_record)
    if len(logs) > 300:
        logs = logs[-300:]
    with open(LEARNING_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)

    print(f"  ✨ [New Skill Mastered]: [{skill_name}] {data.get('title')}")
    print(f"     💡 Rule: {data.get('rule')[:100]}...")
    return learning_record

def start_continuous_learning_loop(interval_minutes: int = 15, model: str = "qwen3:4b"):
    """Runs a continuous background loop that learns whenever internet is available."""
    print("=" * 70)
    print("🧠 AUTONOMOUS CONTINUOUS WEB LEARNING ENGINE ACTIVATED")
    print(f"⏱️ Learning Interval: Every {interval_minutes} minutes when online")
    print("=" * 70)

    while True:
        try:
            if is_connected_to_internet():
                topic = random.choice(RESEARCH_TOPICS)
                learn_from_topic(topic, model=model)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No internet connection. Pausing learning until network reconnects...")
        except Exception as e:
            print(f"Learning cycle error: {e}")

        # Sleep until next research interval
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Web Skill Learner")
    parser.add_argument("--interval", type=int, default=15, help="Minutes between learning cycles (default: 15)")
    parser.add_argument("--once", action="store_true", help="Run a single learning cycle now")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Model to use for synthesis")

    args = parser.parse_args()

    if args.once:
        if is_connected_to_internet():
            topic = random.choice(RESEARCH_TOPICS)
            learn_from_topic(topic, model=args.model)
        else:
            print("No internet connection detected.")
    else:
        start_continuous_learning_loop(interval_minutes=args.interval, model=args.model)
