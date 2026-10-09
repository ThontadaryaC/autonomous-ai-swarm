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
from bs4 import BeautifulSoup
import ollama

import skill_evolver

# Knowledge repository directory for learned playbooks & code templates
PLAYBOOKS_DIR = "c:/Users/cool/Desktop/skills/learned_playbooks"
os.makedirs(PLAYBOOKS_DIR, exist_ok=True)

ADVANCED_CURRICULUM = [
    {
        "category": "auth_and_credentials",
        "topic": "Automated login session handling and CSRF token extraction in Python requests",
        "query": "python requests session login handle csrf token cookies example"
    },
    {
        "category": "auth_and_credentials",
        "topic": "Secure programmatic credential generation and API key management",
        "query": "python generate secure credentials secrets token hash bcrypt"
    },
    {
        "category": "web_scraping_and_automation",
        "topic": "Stealth web scraping techniques headers rotation and anti-bot evasion",
        "query": "python web scraping bypass cloudflare bot detection stealth headers user-agent"
    },
    {
        "category": "web_scraping_and_automation",
        "topic": "Automated web form submission and dynamic response parsing",
        "query": "python beautifulsoup parse form inputs post data extract response"
    },
    {
        "category": "human_verification_and_bot_detection",
        "topic": "Understanding CAPTCHA and Cloudflare challenge mechanisms and automated solving architectures",
        "query": "anti bot challenge mechanisms cloudflare turnstile recaptcha solving techniques python"
    },
    {
        "category": "cybersecurity_defenses",
        "topic": "Preventing credential stuffing and securing automated login endpoints",
        "query": "rate limiting credential stuffing protection secure login endpoint fastapi"
    }
]

def check_internet() -> bool:
    """Checks for active internet connection."""
    try:
        urllib.request.urlopen("https://1.1.1.1", timeout=3)
        return True
    except Exception:
        try:
            urllib.request.urlopen("https://www.google.com", timeout=3)
            return True
        except Exception:
            return False

def scrape_web_documentation(query: str) -> list:
    """Searches and scrapes web documentation for detailed code patterns."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    encoded = urllib.parse.quote_plus(query)
    search_url = f"https://html.duckduckgo.com/html/?q={encoded}"
    
    extracted_knowledge = []
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        
        soup = BeautifulSoup(html, "html.parser")
        snippets = soup.find_all("a", class_="result__snippet")
        for s in snippets[:4]:
            extracted_knowledge.append(s.get_text().strip())
    except Exception as e:
        extracted_knowledge.append(f"Scraping error: {str(e)}")

    return extracted_knowledge

def synthesize_and_save_skill(curriculum_item: dict, model: str = "qwen3:4b") -> dict:
    """Uses LLM to synthesize learned techniques and create runnable playbooks."""
    category = curriculum_item["category"]
    topic = curriculum_item["topic"]
    query = curriculum_item["query"]
    today_str = datetime.date.today().isoformat()
    now_str = datetime.datetime.now().strftime("%H:%M:%S")

    print(f"\n🌐 [{now_str}] Deep Web Learning Active: '{topic}'")
    scraped_data = scrape_web_documentation(query)
    context_text = "\n".join(scraped_data)

    prompt = f"""You are the Autonomous Web Automation & Cybersecurity Skill Evolver.
Analyze the following scraped web intelligence regarding: "{topic}"

SCRAPED DATA:
{context_text}

Provide:
1. A clear breakdown of how this technique works in automated web agents.
2. A working, robust Python code template for this capability.
3. Best practices to handle edge cases (e.g., rate limits, session expiry, security).

Return ONLY valid JSON in this exact schema:
{{
  "title": "Title of Learned Skill",
  "category": "{category}",
  "key_technique": "Summary of technical mechanism",
  "python_code_template": "Executable Python code snippet illustrating the pattern",
  "defense_or_best_practice": "Important security or reliability rule"
}}
"""

    host = os.environ.get("OLLAMA_HOST", "https://catalogue-president-eyes-fairy.trycloudflare.com")
    client = ollama.Client(host=host)

    try:
        resp = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )
        result = json.loads(resp.message.content)
    except Exception:
        result = {
            "title": topic,
            "category": category,
            "key_technique": "Automated session and credential management using requests and BeautifulSoup.",
            "python_code_template": "# Sample Automated Web Session\nimport requests\n\ns = requests.Session()\ns.headers.update({'User-Agent': 'Mozilla/5.0'})\n",
            "defense_or_best_practice": "Always implement exponential backoff and sanitize stored session tokens."
        }

    # Save to persistent Playbooks directory
    filename_safe = re.sub(r'[^a-zA-Z0-9_]', '_', result.get("title", "playbook"))[:40].lower() + ".py"
    playbook_path = os.path.join(PLAYBOOKS_DIR, filename_safe)
    
    code_content = f'"""\nSkill: {result.get("title")}\nCategory: {category}\nDate Learned: {today_str} {now_str}\nKey Technique: {result.get("key_technique")}\nRule: {result.get("defense_or_best_practice")}\n"""\n\n'
    code_content += result.get("python_code_template", "# Code template")
    
    with open(playbook_path, "w", encoding="utf-8") as f:
        f.write(code_content)

    # Update skills_memory.json
    mem = skill_evolver.load_memory()
    if category not in mem["skills"]:
        mem["skills"][category] = {"level": 1, "learnings": []}
    
    mem["skills"][category]["learnings"].append({
        "date": today_str,
        "time": now_str,
        "title": result.get("title"),
        "rule": result.get("defense_or_best_practice"),
        "playbook_file": playbook_path
    })
    mem["skills"][category]["level"] = 1 + (len(mem["skills"][category]["learnings"]) // 2)
    skill_evolver.save_memory(mem)

    print(f"  ✨ [Skill Learned & Playbook Created]: {result.get('title')}")
    print(f"     📁 Playbook saved to: {playbook_path}")
    print(f"     🛡️ Rule: {result.get('defense_or_best_practice')[:90]}...")
    return result

def auto_start_daemon(interval_minutes: int = 10, model: str = "qwen3:4b"):
    """Background loop that watches network connection and auto-learns autonomously."""
    print("=" * 75)
    print("🤖 AUTONOMOUS WEB SCRAPER & SKILL EVOLVER DAEMON ACTIVE")
    print(f"🌐 Auto-Trigger: Activates automatically whenever internet is detected")
    print(f"📁 Playbooks Location: {PLAYBOOKS_DIR}")
    print("=" * 75)

    while True:
        try:
            if check_internet():
                item = random.choice(ADVANCED_CURRICULUM)
                synthesize_and_save_skill(item, model=model)
            else:
                print(f"[{time.strftime('%H:%M:%S')}] Network offline. Waiting for reconnection...")
        except Exception as e:
            print(f"Daemon error: {e}")

        # Wait for next learning interval
        time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Web Scraper & Skill Evolver")
    parser.add_argument("--interval", type=int, default=10, help="Minutes between learning cycles (default: 10)")
    parser.add_argument("--once", action="store_true", help="Run a single learning cycle now")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Model to use for synthesis")

    args = parser.parse_args()

    if args.once:
        if check_internet():
            item = random.choice(ADVANCED_CURRICULUM)
            synthesize_and_save_skill(item, model=args.model)
        else:
            print("No internet connection.")
    else:
        auto_start_daemon(interval_minutes=args.interval, model=args.model)
