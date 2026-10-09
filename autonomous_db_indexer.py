import os
import sys
import sqlite3
import json
import time
import math
import re
from pathlib import Path
from typing import List, Dict, Any

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import requests

DB_PATH = "c:/Users/cool/Desktop/skills/agent_memory.db"

class AutonomousDatabaseIndexer:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initializes SQLite database with FTS5 Full-Text Indexing and Vector Storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Main Knowledge Store Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                code_snippet TEXT,
                tags TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. FTS5 High-Performance Search Index
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(
                title,
                content,
                code_snippet,
                tags,
                content='knowledge_items',
                content_rowid='id'
            )
        """)

        # 3. Triggers for Automatic Index Synchronization
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge_items BEGIN
                INSERT INTO knowledge_fts(rowid, title, content, code_snippet, tags)
                VALUES (new.id, new.title, new.content, new.code_snippet, new.tags);
            END;
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge_items BEGIN
                INSERT INTO knowledge_fts(knowledge_fts, rowid, title, content, code_snippet, tags)
                VALUES('delete', old.id, old.title, old.content, old.code_snippet, old.tags);
            END;
        """)

        conn.commit()
        conn.close()

    def index_document(self, category: str, title: str, content: str, code_snippet: str = "", tags: str = "", source: str = "web_learning") -> int:
        """Indexes a new piece of knowledge, code, or health pattern into the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO knowledge_items (category, title, content, code_snippet, tags, source)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category, title, content, code_snippet, tags, source))

        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id

    def fast_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Performs ultra-fast (<5ms) BM25 full-text indexed search across all stored memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Clean search query for FTS5 syntax
        clean_terms = re.findall(r'\w+', query)
        if not clean_terms:
            conn.close()
            return []
        fts_query = " OR ".join(clean_terms)

        try:
            cursor.execute("""
                SELECT k.id, k.category, k.title, k.content, k.code_snippet, k.tags, k.source, rank
                FROM knowledge_fts f
                JOIN knowledge_items k ON f.rowid = k.id
                WHERE knowledge_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (fts_query, limit))
            
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "id": r[0],
                    "category": r[1],
                    "title": r[2],
                    "content": r[3],
                    "code_snippet": r[4],
                    "tags": r[5],
                    "source": r[6],
                    "score": r[7]
                })
            conn.close()
            return results
        except Exception as e:
            conn.close()
            return []

    def auto_index_all_playbooks(self, playbooks_dir: str = "c:/Users/cool/Desktop/skills/learned_playbooks") -> int:
        """Automatically scans and indexes all generated Python playbooks and learned code."""
        if not os.path.exists(playbooks_dir):
            return 0
        
        count = 0
        for file in os.listdir(playbooks_dir):
            if file.endswith(".py"):
                file_path = os.path.join(playbooks_dir, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                    
                    # Extract header metadata
                    title = file.replace("_", " ").replace(".py", "").title()
                    category = "web_automation"
                    if "health" in file.lower() or "3d" in file.lower():
                        category = "3d_health_graphics"
                    elif "security" in file.lower() or "credential" in file.lower():
                        category = "cybersecurity"

                    self.index_document(
                        category=category,
                        title=title,
                        content=f"Learned playbook file: {file}",
                        code_snippet=code,
                        tags=f"{category}, {title}, python",
                        source=file_path
                    )
                    count += 1
                except Exception:
                    pass
        return count

    def get_stats(self) -> Dict[str, Any]:
        """Returns total indexed items and category breakdowns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM knowledge_items")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT category, COUNT(*) FROM knowledge_items GROUP BY category")
        categories = dict(cursor.fetchall())
        conn.close()
        return {"total_indexed_items": total, "categories": categories}

# Global Indexer Instance
db_indexer = AutonomousDatabaseIndexer()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Fast Database Indexer")
    parser.add_argument("--auto-index", action="store_true", help="Index all playbooks into DB")
    parser.add_argument("--search", type=str, help="Search memory DB")
    parser.add_argument("--stats", action="store_true", help="Show DB statistics")

    args = parser.parse_args()

    if args.auto_index:
        added = db_indexer.auto_index_all_playbooks()
        print(f"✅ Successfully indexed {added} playbooks into High-Speed Database!")
        print("Database Stats:", db_indexer.get_stats())
    elif args.search:
        start_time = time.time()
        results = db_indexer.fast_search(args.search)
        elapsed_ms = (time.time() - start_time) * 1000
        print(f"🔍 Search results for '{args.search}' (Retrieved in {elapsed_ms:.2f} ms):")
        print("=" * 65)
        for r in results:
            print(f"\n📌 [{r['category'].upper()}] {r['title']}")
            if r['code_snippet']:
                print(f"   💻 Code Preview: {r['code_snippet'][:120]}...")
    else:
        print("Database Stats:", db_indexer.get_stats())
