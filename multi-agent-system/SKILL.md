---
name: multi-agent-system
description: Autonomous 3-agent software engineering team with Internet search, URL reading, cybersecurity scanning, code generation, and self-healing QA test execution.
---

# 🤖 Multi-Agent Autonomous Engineering Team

An integrated 3-agent system combining your 3 local Ollama LLMs with real-time internet search, file system access, terminal execution, and cybersecurity audits.

```mermaid
flowchart TD
    UserGoal["🎯 User Project Goal"] --> Agent1["🛡️ Agent 1: Backend & Security<br/>(Model: qwen3:4b)"]
    Agent1 -->|Internet Search, Secure APIs, Auth| Agent2["🎨 Agent 2: Frontend Engineer<br/>(Model: gemma3:4b-it)"]
    Agent2 -->|UI/UX, CSS, Responsive Layout| Agent3["🧪 Agent 3: QA & Test Automation<br/>(Model: llama3.2:latest)"]
    Agent3 -->|Run Tests & Static Security Audit| Decision{"Passed All Checks?"}
    Decision -- "❌ Errors / Security Flaws Found" -->|Structured QA Bug Report| Agent1
    Decision -- "✅ STATUS: PASSED" --> Success["🎉 Production-Ready Verified App"]
```

---

## 🛠️ Full Toolset Equipped Across All Agents

### 🌐 1. Internet & Live Web Tools
- **`search_internet(query)`**: Searches DuckDuckGo for live API documentation, syntax examples, and library references.
- **`fetch_url_content(url)`**: Extracts text and documentation directly from web pages and API docs.

### 💻 2. Built-in Coding & File Tools
- **`read_file(path)`**: Reads project files.
- **`write_file(path, content)`**: Creates or updates files.
- **`replace_in_file(path, target, replacement)`**: Precise code modifications.
- **`list_files(path)`**: Lists directories and workspace files.

### 🛡️ 3. Cybersecurity & Terminal Tools
- **`security_audit_scan(path)`**: Static code analysis checking for hardcoded secrets, SQLi, XSS, and command injection.
- **`run_command(command)`**: Executes terminal commands, tests, linters, and python scripts.

---

## 🚀 How to Run

### Interactive Mode:
```powershell
python c:\Users\cool\Desktop\skills\multi_agent_team.py
```

### Direct Goal:
```powershell
python c:\Users\cool\Desktop\skills\multi_agent_team.py --goal "Build a secure weather dashboard web app with API fetching, clean CSS, and automated tests"
```
