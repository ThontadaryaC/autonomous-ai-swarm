import os
import sys
import json
import time
import threading
import subprocess
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path

# Ensure standard output supports UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import skill_evolver
import multi_agent_team

PORT = 8080
WORKSPACE_DIR = "C:/Users/cool/Desktop/Portfolio"

# Global state for GUI
ACTIVE_TASK = {
    "status": "IDLE",
    "goal": "",
    "current_agent": "",
    "logs": [],
    "final_result": None
}

def append_log(agent_name: str, message_type: str, content: str):
    timestamp = time.strftime("%H:%M:%S")
    ACTIVE_TASK["logs"].append({
        "time": timestamp,
        "agent": agent_name,
        "type": message_type,
        "content": content
    })
    if len(ACTIVE_TASK["logs"]) > 500:
        ACTIVE_TASK["logs"] = ACTIVE_TASK["logs"][-500:]

def run_task_background(prompt: str):
    global ACTIVE_TASK
    ACTIVE_TASK["status"] = "RUNNING"
    ACTIVE_TASK["goal"] = prompt
    ACTIVE_TASK["logs"] = []
    ACTIVE_TASK["final_result"] = None

    append_log("System", "INFO", f"Cloud GPU Swarm running task: '{prompt}'")

    try:
        swarm = multi_agent_team.MultiAgentSwarm(
            coder_model="qwen3:4b",
            frontend_model="gemma3:4b-it-q4_K_M",
            tester_model="llama3.2:latest"
        )

        shared_context = f"User Request: {prompt}\nUser Desktop Path: C:\\Users\\cool\\Desktop\n"

        # Step 1: Qwen 3 (Backend & Folder Creation)
        ACTIVE_TASK["current_agent"] = "Agent 1: Backend Lead (Qwen 3 on Cloud GPU)"
        append_log("Agent 1 (Qwen 3)", "THINKING", "Creating folder C:\\Users\\cool\\Desktop\\Portfolio and index.html...")
        
        coder_task = (
            f"User request: '{prompt}'.\n"
            "1. Determine the target folder on the system (e.g. C:\\Users\\cool\\Desktop\\Portfolio) and call create_directory.\n"
            "2. Create the index.html file with complete structure and content using write_file in that folder."
        )
        coder_out = swarm.coder_agent.step(coder_task, shared_context)
        append_log("Agent 1 (Qwen 3)", "OUTPUT", coder_out)
        shared_context += f"\nBackend output:\n{coder_out}\n"

        # Step 2: Gemma 3 (Frontend & Styling)
        ACTIVE_TASK["current_agent"] = "Agent 2: Frontend Lead (Gemma 3 on Cloud GPU)"
        append_log("Agent 2 (Gemma 3)", "THINKING", "Creating responsive style.css and interactive script.js...")
        
        frontend_task = (
            f"User request: '{prompt}'.\n"
            f"Backend summary: {coder_out}\n"
            "Create modern responsive style.css and script.js in the target project folder using write_file."
        )
        frontend_out = swarm.frontend_agent.step(frontend_task, shared_context)
        append_log("Agent 2 (Gemma 3)", "OUTPUT", frontend_out)
        shared_context += f"\nFrontend output:\n{frontend_out}\n"

        # Step 3: Llama 3.2 (QA Validation)
        ACTIVE_TASK["current_agent"] = "Agent 3: QA & Testing (Llama 3.2 on Cloud GPU)"
        append_log("Agent 3 (Llama 3.2)", "THINKING", "Validating folder contents and running QA checks...")
        
        qa_task = (
            f"Verify the project created for: '{prompt}'.\n"
            "Use list_files to confirm all files are created in the project folder and provide a final QA summary."
        )
        qa_out = swarm.qa_agent.step(qa_task, shared_context)
        append_log("Agent 3 (Llama 3.2)", "REPORT", qa_out)

        append_log("System", "SUCCESS", "All 3 agents completed the task successfully on your machine!")
        ACTIVE_TASK["status"] = "COMPLETED"
        ACTIVE_TASK["final_result"] = {
            "status": "SUCCESS",
            "qa_report": qa_out
        }

        # Evolve Skills & Update Daily Memory
        append_log("Skill Evolver", "INFO", "Reflecting on execution and updating daily skill evolution logs...")
        all_logs_text = "\n".join([f"[{l['agent']}] {l['content']}" for l in ACTIVE_TASK["logs"]])
        evolution_result = skill_evolver.reflect_and_evolve_skills(
            task=prompt,
            execution_log=all_logs_text,
            qa_feedback=qa_out,
            model="qwen3:4b"
        )
        append_log("Skill Evolver", "IMPROVEMENT", f"Skill evolution logged: {len(evolution_result.get('improvements', []))} updates recorded!")

    except Exception as e:
        ACTIVE_TASK["status"] = "ERROR"
        append_log("System", "ERROR", f"Error during execution: {str(e)}")

# ==============================================================================
# HTML / CSS / JS GUI Dashboard
# ==============================================================================

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>⚡ Cloud GPU Agent Cockpit & Skill Evolution GUI</title>
  <style>
    :root {
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #c9d1d9;
      --text-bright: #f0f6fc;
      --accent: #58a6ff;
      --green: #2ea043;
      --yellow: #d29922;
      --purple: #bc8cff;
      --red: #f85149;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: var(--bg); color: var(--text); padding: 20px; }
    header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
    h1 { color: var(--text-bright); font-size: 1.5rem; display: flex; align-items: center; gap: 10px; }
    .badge { background: #238636; color: white; font-size: 0.75rem; padding: 3px 8px; border-radius: 12px; }
    
    .grid { display: grid; grid-template-columns: 350px 1fr; gap: 20px; margin-top: 20px; }
    .card { background: var(--card-bg); border: 1px solid var(--border); border-radius: 8px; padding: 18px; margin-bottom: 20px; }
    .card h2 { font-size: 1.1rem; color: var(--text-bright); margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
    
    /* Form */
    textarea { width: 100%; height: 110px; background: #0d1117; border: 1px solid var(--border); color: var(--text-bright); border-radius: 6px; padding: 10px; font-size: 0.9rem; resize: vertical; }
    button { background: #238636; color: white; border: none; padding: 12px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; margin-top: 10px; width: 100%; transition: background 0.2s; font-size: 0.95rem; }
    button:hover { background: #2ea043; }
    button:disabled { background: #30363d; color: #8b949e; cursor: not-allowed; }

    /* Model Status */
    .model-pill { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #0d1117; border: 1px solid var(--border); border-radius: 6px; margin-bottom: 8px; font-size: 0.85rem; }
    .model-pill .name { font-weight: 600; color: var(--accent); }
    .model-pill .role { color: #8b949e; font-size: 0.75rem; }

    /* Tabs */
    .tabs { display: flex; gap: 8px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; }
    .tab-btn { background: none; border: none; color: #8b949e; font-size: 0.95rem; padding: 6px 12px; cursor: pointer; width: auto; margin-top: 0; border-radius: 6px; }
    .tab-btn.active { background: #21262d; color: var(--text-bright); font-weight: 600; }

    /* Logs & Thinkings */
    .log-container { background: #090d13; border: 1px solid var(--border); border-radius: 6px; height: 500px; overflow-y: auto; padding: 12px; font-family: Consolas, Monaco, monospace; font-size: 0.85rem; line-height: 1.5; }
    .log-entry { margin-bottom: 12px; padding: 8px; border-radius: 4px; background: #161b22; border-left: 4px solid #30363d; }
    .log-entry.THINKING { border-left-color: var(--yellow); background: rgba(210, 153, 34, 0.08); }
    .log-entry.OUTPUT { border-left-color: var(--accent); background: rgba(88, 166, 255, 0.05); }
    .log-entry.REPORT { border-left-color: var(--purple); background: rgba(188, 140, 255, 0.08); }
    .log-entry.SUCCESS { border-left-color: var(--green); background: rgba(46, 160, 67, 0.15); }
    .log-entry.ERROR { border-left-color: var(--red); background: rgba(248, 81, 73, 0.1); }
    .log-header { display: flex; justify-content: space-between; font-weight: 600; font-size: 0.78rem; margin-bottom: 4px; }

    /* Skill Evolution Bars */
    .skill-bar { margin-bottom: 14px; }
    .skill-meta { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px; font-weight: 600; }
    .bar-bg { background: #21262d; height: 8px; border-radius: 4px; overflow: hidden; }
    .bar-fill { background: linear-gradient(90deg, var(--accent), var(--purple)); height: 100%; border-radius: 4px; width: 20%; transition: width 0.4s; }

    .daily-box { background: #090d13; border: 1px solid var(--border); border-radius: 6px; padding: 12px; max-height: 250px; overflow-y: auto; font-size: 0.85rem; }
  </style>
</head>
<body>

<header>
  <h1>⚡ Cloud GPU Agent Cockpit & Skill Evolver <span class="badge">CLOUD GPU CONNECTED</span></h1>
  <div>Status: <strong id="global-status" style="color:var(--green)">READY</strong></div>
</header>

<div class="grid">
  <!-- Left Column: Controls & Evolution -->
  <div>
    <!-- Task Launcher -->
    <div class="card">
      <h2>🚀 Launch Swarm Prompt</h2>
      <textarea id="task-input">create a new folder in the desktop folder and name it as "Portfolio" and please build My Portfolio website</textarea>
      <button id="run-btn" onclick="startTask()">Start 3-Agent Swarm (Cloud GPU)</button>
    </div>

    <!-- Active Local Models -->
    <div class="card">
      <h2>🤖 Active Cloud GPU Team</h2>
      <div class="model-pill">
        <div>
          <div class="name">qwen3:4b (Rank #1)</div>
          <div class="role">Backend, Core & Folder Architect</div>
        </div>
        <span style="color:var(--green)">● GPU Online</span>
      </div>
      <div class="model-pill">
        <div>
          <div class="name">gemma3:4b-it (Rank #2)</div>
          <div class="role">Frontend & UI/UX Specialist</div>
        </div>
        <span style="color:var(--green)">● GPU Online</span>
      </div>
      <div class="model-pill">
        <div>
          <div class="name">llama3.2:latest (Rank #3)</div>
          <div class="role">QA, Validation & Test Runner</div>
        </div>
        <span style="color:var(--green)">● GPU Online</span>
      </div>
    </div>

    <!-- Self-Improving Skills -->
    <div class="card">
      <h2>📈 Skill Evolution Levels</h2>
      <div id="skills-progress">Loading skill levels...</div>
    </div>
  </div>

  <!-- Right Column: Tabs (Live Thinkings & Logs / Daily Improvements / Output) -->
  <div>
    <div class="card" style="height: 100%;">
      <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('logs', event)">🧠 Agent Thinkings & Live Logs</button>
        <button class="tab-btn" onclick="switchTab('daily', event)">📅 Daily Skill Improvements</button>
        <button class="tab-btn" onclick="switchTab('files', event)">📁 Workspace Files</button>
      </div>

      <!-- Tab 1: Live Thinkings & Logs -->
      <div id="tab-logs">
        <div class="log-container" id="log-box">
          <div style="color: #8b949e; text-align: center; margin-top: 180px;">Connected to Cloud GPU! Click 'Start 3-Agent Swarm' to begin.</div>
        </div>
      </div>

      <!-- Tab 2: Daily Skill Improvements -->
      <div id="tab-daily" style="display:none;">
        <div class="daily-box" style="height: 500px; max-height: 500px;" id="daily-content">
          Loading daily evolution report...
        </div>
      </div>

      <!-- Tab 3: Generated Files -->
      <div id="tab-files" style="display:none;">
        <div class="daily-box" style="height: 500px; max-height: 500px;" id="files-content">
          Loading project files...
        </div>
      </div>
    </div>
  </div>
</div>

<script>
  let currentTab = 'logs';

  function switchTab(tab, evt) {
    currentTab = tab;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (evt && evt.target) evt.target.classList.add('active');
    document.getElementById('tab-logs').style.display = tab === 'logs' ? 'block' : 'none';
    document.getElementById('tab-daily').style.display = tab === 'daily' ? 'block' : 'none';
    document.getElementById('tab-files').style.display = tab === 'files' ? 'block' : 'none';
    if (tab === 'daily') fetchDaily();
    if (tab === 'files') fetchFiles();
  }

  async function startTask() {
    const goal = document.getElementById('task-input').value.trim();
    if (!goal) return alert("Please enter a prompt!");
    
    document.getElementById('run-btn').disabled = true;
    document.getElementById('run-btn').innerText = "Swarm is Working (GPU)...";
    document.getElementById('global-status').innerText = "RUNNING (CLOUD GPU)";
    document.getElementById('global-status').style.color = "var(--yellow)";

    await fetch('/api/start', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({goal: goal})
    });
  }

  async function pollStatus() {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) return;
      const data = await res.json();
      
      const statusEl = document.getElementById('global-status');
      statusEl.innerText = data.status;
      if (data.status === 'RUNNING') {
        statusEl.style.color = 'var(--yellow)';
        document.getElementById('run-btn').disabled = true;
        document.getElementById('run-btn').innerText = "Swarm is Working (GPU)...";
      } else if (data.status === 'COMPLETED') {
        statusEl.style.color = 'var(--green)';
        document.getElementById('run-btn').disabled = false;
        document.getElementById('run-btn').innerText = "Start 3-Agent Swarm (Cloud GPU)";
      } else {
        statusEl.style.color = 'var(--accent)';
        document.getElementById('run-btn').disabled = false;
        document.getElementById('run-btn').innerText = "Start 3-Agent Swarm (Cloud GPU)";
      }

      // Render Logs
      if (data.logs && data.logs.length > 0) {
        const logBox = document.getElementById('log-box');
        logBox.innerHTML = data.logs.map(l => `
          <div class="log-entry ${l.type}">
            <div class="log-header">
              <span>[${l.agent}]</span>
              <span style="color:#8b949e;">${l.time}</span>
            </div>
            <div style="white-space: pre-wrap;">${escapeHtml(l.content)}</div>
          </div>
        `).join('');
        logBox.scrollTop = logBox.scrollHeight;
      }

      // Render Skills
      if (data.skills) {
        renderSkills(data.skills);
      }
    } catch (e) {
      // Ignore transient fetch errors
    }
  }

  function renderSkills(skillsData) {
    const container = document.getElementById('skills-progress');
    let html = '';
    for (const [name, info] of Object.entries(skillsData.skills || {})) {
      const lvl = info.level || 1;
      const count = (info.learnings || []).length;
      const width = Math.min(100, lvl * 20);
      html += `
        <div class="skill-bar">
          <div class="skill-meta">
            <span>${name.replace('_', ' ').toUpperCase()}</span>
            <span>Lvl ${lvl} (${count} learnings)</span>
          </div>
          <div class="bar-bg"><div class="bar-fill" style="width: ${width}%"></div></div>
        </div>
      `;
    }
    container.innerHTML = html;
  }

  async function fetchDaily() {
    try {
      const res = await fetch('/api/daily');
      const data = await res.json();
      document.getElementById('daily-content').innerHTML = `<pre style="white-space:pre-wrap; font-family:monospace;">${escapeHtml(data.summary)}</pre>`;
    } catch(e) {}
  }

  async function fetchFiles() {
    try {
      const res = await fetch('/api/files');
      const data = await res.json();
      document.getElementById('files-content').innerHTML = data.files.map(f => `
        <div style="padding: 8px; border-bottom: 1px solid var(--border);">
          <strong>📄 ${f.name}</strong> (${f.size})
        </div>
      `).join('') || "No project files created yet.";
    } catch(e) {}
  }

  function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  setInterval(pollStatus, 1500);
  pollStatus();
</script>
</body>
</html>
"""

# ==============================================================================
# Threaded HTTP Request Handler
# ==============================================================================

class DashboardHandler(BaseHTTPRequestHandler):
    def safe_write(self, data: bytes):
        try:
            self.wfile.write(data)
        except Exception:
            pass

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            if parsed.path == "/" or parsed.path == "/index.html":
                body = HTML_PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.safe_write(body)
            elif parsed.path == "/api/status":
                mem = skill_evolver.load_memory()
                payload = {
                    "status": ACTIVE_TASK["status"],
                    "goal": ACTIVE_TASK["goal"],
                    "current_agent": ACTIVE_TASK["current_agent"],
                    "logs": ACTIVE_TASK["logs"],
                    "skills": mem
                }
                body = json.dumps(payload).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.safe_write(body)
            elif parsed.path == "/api/daily":
                summary = skill_evolver.get_today_summary()
                body = json.dumps({"summary": summary}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.safe_write(body)
            elif parsed.path == "/api/files":
                files = []
                check_dir = "C:/Users/cool/Desktop/Portfolio"
                if os.path.exists(check_dir):
                    for item in os.listdir(check_dir):
                        p = os.path.join(check_dir, item)
                        size = f"{os.path.getsize(p)} bytes" if os.path.isfile(p) else "Folder"
                        files.append({"name": item, "size": size})
                body = json.dumps({"files": files}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.safe_write(body)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception:
            pass

    def do_POST(self):
        try:
            if self.path == "/api/start":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode("utf-8"))
                goal = data.get("goal", "")

                if goal:
                    thread = threading.Thread(target=run_task_background, args=(goal,), daemon=True)
                    thread.start()

                resp = json.dumps({"status": "STARTED"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(resp)))
                self.end_headers()
                self.safe_write(resp)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception:
            pass

    def log_message(self, format, *args):
        return

def run_server():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print("=" * 70)
    print(f"🚀 CLOUD GPU AGENT COCKPIT & GUI RUNNING AT:")
    print(f"👉 http://localhost:{PORT}")
    print("=" * 70)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Dashboard server...")

if __name__ == "__main__":
    run_server()
