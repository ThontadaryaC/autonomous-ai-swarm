import os
import sys
import json
import datetime
import urllib.request
import xml.etree.ElementTree as ET
import re

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import skill_evolver
import ollama

def fetch_live_news(country_code: str = "US", topic: str = None) -> list:
    """Fetches real-time live top news headlines from Google News RSS.
    Args:
        country_code: 'US' for USA, 'IN' for India.
        topic: Optional topic filter (e.g. 'TECHNOLOGY', 'BUSINESS', 'WORLD')
    """
    try:
        if topic:
            url = f"https://news.google.com/rss/headlines/section/topic/{topic.upper()}?hl=en-{country_code}&gl={country_code}&ceid={country_code}:en"
        else:
            url = f"https://news.google.com/rss?hl=en-{country_code}&gl={country_code}&ceid={country_code}:en"
        
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            xml_data = r.read()
        
        root = ET.fromstring(xml_data)
        items = []
        for item in root.findall(".//item")[:6]:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
            
            # Clean title
            clean_title = re.sub(r'\s+-\s+.*$', '', title).strip()
            source = title.split("-")[-1].strip() if "-" in title else "News Source"
            items.append({
                "headline": clean_title,
                "source": source,
                "date": pub_date,
                "link": link
            })
        return items
    except Exception as e:
        return [{"headline": f"Error fetching news: {str(e)}", "source": "System", "link": ""}]

def get_usa_news_summary() -> str:
    """Returns top interesting news in the USA."""
    news = fetch_live_news(country_code="US")
    tech_news = fetch_live_news(country_code="US", topic="TECHNOLOGY")
    
    today_str = datetime.date.today().isoformat()
    lines = [f"🇺🇸 Top & Most Interesting News in the USA ({today_str}):", "=" * 60]
    
    lines.append("\n📌 Top Headlines:")
    for i, item in enumerate(news[:4], 1):
        lines.append(f"  {i}. {item['headline']} ({item['source']})")
    
    lines.append("\n🚀 Trending Tech & AI in the USA:")
    for i, item in enumerate(tech_news[:3], 1):
        lines.append(f"  • {item['headline']} ({item['source']})")
    
    return "\n".join(lines)

def get_india_news_summary() -> str:
    """Returns top interesting news in India."""
    news = fetch_live_news(country_code="IN")
    tech_news = fetch_live_news(country_code="IN", topic="TECHNOLOGY")
    
    today_str = datetime.date.today().isoformat()
    lines = [f"🇮🇳 Top & Most Interesting News in India ({today_str}):", "=" * 60]
    
    lines.append("\n📌 Top Headlines:")
    for i, item in enumerate(news[:4], 1):
        lines.append(f"  {i}. {item['headline']} ({item['source']})")
    
    lines.append("\n🚀 Tech, Startups & Innovation in India:")
    for i, item in enumerate(tech_news[:3], 1):
        lines.append(f"  • {item['headline']} ({item['source']})")
    
    return "\n".join(lines)

def get_daily_briefing() -> str:
    """Generates an all-in-one daily briefing: Skills learned today + USA news + India news."""
    today_str = datetime.date.today().isoformat()
    skill_update = skill_evolver.get_today_summary()
    usa_news = get_usa_news_summary()
    india_news = get_india_news_summary()
    
    briefing = [
        "*" * 70,
        f"🌟 AGENT DAILY INTELLIGENCE & SKILLS BRIEFING ({today_str})",
        "*" * 70,
        "",
        "🧠 1. DAILY SKILL IMPROVEMENTS & LEARNED PLAYBOOKS:",
        skill_update,
        "",
        "-" * 70,
        "🌍 2. LIVE GLOBAL NEWS & TRENDING INTELLIGENCE:",
        "",
        usa_news,
        "",
        india_news,
        "",
        "*" * 70
    ]
    return "\n".join(briefing)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1].lower()
        if "usa" in query or "us" in query:
            print(get_usa_news_summary())
        elif "india" in query or "in" in query:
            print(get_india_news_summary())
        elif "skill" in query:
            print(skill_evolver.get_today_summary())
        else:
            print(get_daily_briefing())
    else:
        print(get_daily_briefing())
