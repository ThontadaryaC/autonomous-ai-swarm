---
name: skill-evolution-and-gui
description: Self-improving meta-learning engine for local LLMs that tracks daily skill improvements and provides a real-time Web GUI dashboard to analyze agent thinkings, tasks, and execution logs.
---

# 🧠 Skill Evolver & Agent Cockpit GUI

This skill adds continuous meta-learning, automatic skill level progression, daily improvement updates, and a visual Web GUI for local LLMs.

---

## 🌟 Key Features

1. **Meta-Learning & Skill Self-Improvement (`skill_evolver.py`)**:
   - Analyzes every task run, extracts lessons learned, and increases mastery levels across 5 core skills:
     - `backend_coding`
     - `cybersecurity`
     - `frontend_ui`
     - `qa_testing`
     - `system_file_access`
   - Records bug patterns to prevent repeat mistakes in future tasks.
   - Logs daily skill progress in `daily_skill_log.json` and persistent memory in `skills_memory.json`.

2. **Daily Updates**:
   - Run `python skill_evolver.py` to see today's improvement report:
     - New skills improved today
     - Code patterns and defense rules learned
     - Current skill levels and total tasks mastered

3. **Interactive Web GUI Cockpit (`dashboard.py`)**:
   - Access at `http://localhost:8080`.
   - **Task Launcher**: Type prompts and start the 3-agent swarm with one click.
   - **Live Thinkings & Logs**: Watch Agent 1, 2, and 3 think, execute tools, and exchange bug reports in real-time.
   - **Skill Evolution Visualizer**: Real-time progress bars showing skill leveling up.
   - **Daily Improvements Viewer**: Inspect today's lessons directly in the browser.
   - **File Explorer**: Browse generated code and project output.

---

## 🚀 How to Launch the GUI

```powershell
python c:\Users\cool\Desktop\skills\dashboard.py
```
Open **`http://localhost:8080`** in any web browser!
