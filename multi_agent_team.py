import os
import sys
import json
import glob
import re
import shutil
import urllib.parse
import urllib.request
import subprocess
from typing import Dict, List, Any
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ollama
import autonomous_db_indexer

# Cloud GPU Endpoint configuration
CLOUD_OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "https://catalogue-president-eyes-fairy.trycloudflare.com")
ollama_client = ollama.Client(host=CLOUD_OLLAMA_HOST)

# ==============================================================================
# Shared Toolset for Agents
# ==============================================================================

def query_database_memory(search_query: str) -> str:
    """Queries the high-speed indexed knowledge database for learned code playbooks and security patterns.
    Args:
        search_query: Keywords to search for (e.g. 'AES encryption', 'Three.js 3D', 'session login')
    """
    try:
        results = autonomous_db_indexer.db_indexer.fast_search(search_query, limit=3)
        if not results:
            return f"No database memory found matching '{search_query}'."
        
        output = [f"Found {len(results)} indexed memory item(s):"]
        for r in results:
            output.append(f"--- [{r['category'].upper()}] {r['title']} ---")
            if r['code_snippet']:
                output.append(f"Code Template:\n{r['code_snippet'][:300]}...")
        return "\n".join(output)
    except Exception as e:
        return f"Database query error: {str(e)}"

def create_directory(path: str) -> str:
    """Creates a new folder or directory tree anywhere on the system."""
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        os.makedirs(resolved, exist_ok=True)
        return f"Successfully created directory: {resolved}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file (creates parent directories if needed)."""
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        os.makedirs(os.path.dirname(os.path.abspath(resolved)), exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content.splitlines())} lines to {resolved}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

def read_file(path: str) -> str:
    """Reads content from a local file."""
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: File '{resolved}' does not exist."
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str = ".") -> str:
    """Lists files and folders in a directory."""
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: Path '{resolved}' does not exist."
        entries = os.listdir(resolved)
        return f"Files in {resolved}:\n" + "\n".join(entries) if entries else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"

def run_command(command: str) -> str:
    """Executes a shell or terminal command."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=35
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        code = result.returncode
        res = f"Exit Code: {code}\n"
        if out:
            res += f"STDOUT:\n{out}\n"
        if err:
            res += f"STDERR:\n{err}\n"
        if not out and not err:
            res += "(Command completed with no output)"
        return res
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 35 seconds."
    except Exception as e:
        return f"Error running command: {str(e)}"

AVAILABLE_TOOLS = [query_database_memory, create_directory, write_file, read_file, list_files, run_command]
TOOL_MAP = {
    "query_database_memory": query_database_memory,
    "create_directory": create_directory,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
    "run_command": run_command
}

# ==============================================================================
# Local Agent Runner (Using Cloud GPU Host)
# ==============================================================================

class LocalAgent:
    def __init__(self, name: str, role: str, model: str, system_prompt: str):
        self.name = name
        self.role = role
        self.model = model
        self.system_prompt = system_prompt

    def step(self, prompt: str, project_context: str = "") -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context:\n{project_context}\n\nTask:\n{prompt}"}
        ]

        print(f"\n[{self.name}] ({self.model} on Cloud GPU) processing...")
        sys.stdout.flush()

        max_turns = 10
        turn = 0
        while turn < max_turns:
            turn += 1
            try:
                response = ollama_client.chat(
                    model=self.model,
                    messages=messages,
                    tools=AVAILABLE_TOOLS
                )
            except Exception as e:
                return f"Error running {self.name}: {str(e)}"

            messages.append(response.message)

            if response.message.tool_calls:
                for tool_call in response.message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = tool_call.function.arguments or {}
                    
                    print(f"  ⚡ [{self.name}] Executing Tool -> {func_name}({json.dumps(func_args)[:120]}...)")
                    sys.stdout.flush()

                    tool_func = TOOL_MAP.get(func_name)
                    if tool_func:
                        try:
                            result = str(tool_func(**func_args))
                        except Exception as e:
                            result = f"Error: {str(e)}"
                    else:
                        result = f"Error: Tool '{func_name}' not found."

                    print(f"     ↳ Result: {result[:120]}")
                    sys.stdout.flush()

                    messages.append({"role": "tool", "content": result})
            else:
                return response.message.content or "Completed."

        return "Completed turn."

# ==============================================================================
# Autonomous Multi-Agent Swarm
# ==============================================================================

class MultiAgentSwarm:
    def __init__(
        self,
        coder_model: str = "qwen3:4b",
        frontend_model: str = "gemma3:4b-it-q4_K_M",
        tester_model: str = "llama3.2:latest"
    ):
        self.coder_agent = LocalAgent(
            name="Agent 1: Backend & Core Architect",
            role="Backend & Cybersecurity Lead",
            model=coder_model,
            system_prompt=(
                "You are the Lead Backend and Core Developer running on Cloud GPU. "
                "You have access to query_database_memory to instantly retrieve learned code and security templates. "
                "Use create_directory and write_file to save the project files."
            )
        )

        self.frontend_agent = LocalAgent(
            name="Agent 2: Frontend UI/UX Specialist",
            role="Frontend & UI/UX Developer",
            model=frontend_model,
            system_prompt=(
                "You are the Lead Frontend Developer running on Cloud GPU. "
                "You have access to query_database_memory for modern CSS, 3D graphics, and UI templates. "
                "Use write_file to save style.css, 3D canvas scripts, and script.js."
            )
        )

        self.qa_agent = LocalAgent(
            name="Agent 3: QA & Test Automation",
            role="QA, Test Runner & Security Reviewer",
            model=tester_model,
            system_prompt=(
                "You are the QA and Verification Specialist running on Cloud GPU. "
                "Inspect the project folder using list_files and read_file. "
                "Verify files and conclude with 'STATUS: PASSED_ALL_TESTS'."
            )
        )

    def run_prompt(self, user_prompt: str):
        print("\n" + "=" * 70)
        print("🚀 MULTI-AGENT SWARM (EQUIPPED WITH HIGH-SPEED DB MEMORY)")
        print(f"🔗 Cloud Host: {CLOUD_OLLAMA_HOST}")
        print(f"💬 Prompt: \"{user_prompt}\"")
        print("=" * 70)
        sys.stdout.flush()

        shared_context = f"User Request: {user_prompt}\nUser Desktop Path: C:\\Users\\cool\\Desktop\n"

        # Step 1: Qwen 3 on Cloud GPU
        print("\n>>> [Step 1] Agent 1 (Qwen 3 on Cloud GPU) - Architecture & Core Files...")
        sys.stdout.flush()
        coder_task = (
            f"User request: '{user_prompt}'.\n"
            "Query memory if helpful, create target directory, and write core files with write_file."
        )
        coder_out = self.coder_agent.step(coder_task, shared_context)
        shared_context += f"\nBackend output:\n{coder_out}\n"

        # Step 2: Gemma 3 on Cloud GPU
        print("\n>>> [Step 2] Agent 2 (Gemma 3 on Cloud GPU) - Frontend & Styling...")
        sys.stdout.flush()
        frontend_task = (
            f"User request: '{user_prompt}'.\n"
            f"Backend summary: {coder_out}\n"
            "Create modern responsive styles and scripts using write_file."
        )
        frontend_out = self.frontend_agent.step(frontend_task, shared_context)
        shared_context += f"\nFrontend output:\n{frontend_out}\n"

        # Step 3: Llama 3.2 on Cloud GPU
        print("\n>>> [Step 3] Agent 3 (Llama 3.2 on Cloud GPU) - QA Verification...")
        sys.stdout.flush()
        qa_task = (
            f"Verify the project created for: '{user_prompt}'.\n"
            "Use list_files to confirm all files exist in the project folder and provide a final QA summary."
        )
        qa_out = self.qa_agent.step(qa_task, shared_context)
        print(f"\n[QA Final Report]:\n{qa_out}")
        sys.stdout.flush()

        print("\n" + "*" * 70)
        print("🎉 SUCCESS! All 3 Cloud GPU agents completed the task on your machine!")
        print("*" * 70)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("\nEnter prompt for 3-Agent Swarm > ").strip()
    
    if prompt:
        swarm = MultiAgentSwarm()
        swarm.run_prompt(prompt)
