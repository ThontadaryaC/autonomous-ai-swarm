import os
import sys
import glob
import subprocess
import traceback
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ollama

# ==========================================
# Coding Agent Tools
# ==========================================

def read_code_file(path: str, start_line: int = 1, end_line: int = 200) -> str:
    """Reads lines from a source code or project file.
    Args:
        path: Path to the file.
        start_line: Starting line number (1-indexed, default: 1).
        end_line: Ending line number (default: 200).
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: File '{resolved}' does not exist."
        if os.path.isdir(resolved):
            return f"Error: '{resolved}' is a directory, not a file."
        
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        
        total_lines = len(all_lines)
        start_idx = max(0, start_line - 1)
        end_idx = min(total_lines, end_line)
        
        selected = all_lines[start_idx:end_idx]
        output = [f"{i + start_idx + 1:4d} | {line}" for i, line in enumerate(selected)]
        
        summary = f"--- {resolved} (Showing lines {start_idx + 1}-{end_idx} of {total_lines}) ---\n"
        return summary + "".join(output)
    except Exception as e:
        return f"Error reading file: {str(e)}"

def write_code_file(path: str, content: str) -> str:
    """Creates or overwrites a source code file.
    Args:
        path: Path where the file should be created.
        content: The code content to write.
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        os.makedirs(os.path.dirname(os.path.abspath(resolved)), exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content.splitlines())} lines to {resolved}."
    except Exception as e:
        return f"Error writing file: {str(e)}"

def replace_in_file(path: str, target_code: str, replacement_code: str) -> str:
    """Replaces a specific block of code in an existing file.
    Args:
        path: Path to the target file.
        target_code: Exact code snippet to find and replace.
        replacement_code: The new code to insert in its place.
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: File '{resolved}' not found."
        
        with open(resolved, "r", encoding="utf-8") as f:
            content = f.read()
        
        if target_code not in content:
            return f"Error: Target code snippet not found in {resolved}. Make sure whitespace and formatting match exactly."
        
        updated_content = content.replace(target_code, replacement_code, 1)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        return f"Successfully replaced code snippet in {resolved}."
    except Exception as e:
        return f"Error replacing in file: {str(e)}"

def search_codebase(directory: str = ".", keyword: str = "") -> str:
    """Searches for a keyword or function/class name in files across a directory.
    Args:
        directory: Directory to search in.
        keyword: The word or token to search for.
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(directory))
        if not os.path.exists(resolved):
            return f"Error: Path '{resolved}' does not exist."
        
        matches = []
        for root, dirs, files in os.walk(resolved):
            # Skip hidden and cache folders
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ["__pycache__", "node_modules", "venv", "env"]]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".json", ".md", ".cpp", ".c", ".h", ".rs", ".go", ".java"]:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            for i, line in enumerate(f, 1):
                                if keyword.lower() in line.lower():
                                    matches.append(f"{file_path}:{i} - {line.strip()[:100]}")
                                    if len(matches) >= 30:
                                        break
                    except Exception:
                        pass
                if len(matches) >= 30:
                    break
            if len(matches) >= 30:
                break
        
        if not matches:
            return f"No matches found for '{keyword}' in {resolved}."
        return f"Found {len(matches)} match(es):\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching codebase: {str(e)}"

def run_command(command: str) -> str:
    """Executes a shell command (e.g. python script.py, pytest, git status, etc.).
    Args:
        command: The command line string to run.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
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
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

# Tool registration
CODING_TOOLS = [read_code_file, write_code_file, replace_in_file, search_codebase, run_command]
TOOL_MAP = {
    "read_code_file": read_code_file,
    "write_code_file": write_code_file,
    "replace_in_file": replace_in_file,
    "search_codebase": search_codebase,
    "run_command": run_command
}

SYSTEM_PROMPT = """You are an autonomous AI Coding Agent.
You have tools to:
1. Inspect code: read_code_file, search_codebase
2. Modify/Create code: write_code_file, replace_in_file
3. Execute and test code: run_command

Workflow:
- When asked to create, fix, or refactor code, use your tools directly.
- Inspect existing files before editing them.
- Always run and test your code using run_command to verify it works without syntax or runtime errors.
- If errors occur, analyze the error output and fix them until the task succeeds.
"""

def run_coding_agent(task_prompt: str, model: str = "qwen3:4b", max_steps: int = 15, verbose: bool = True) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task_prompt}
    ]

    for step in range(1, max_steps + 1):
        if verbose:
            print(f"\n[Step {step}/{max_steps}] Querying model: {model} ...")

        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                tools=CODING_TOOLS
            )
        except Exception as e:
            return f"Model execution error: {str(e)}"

        messages.append(response.message)

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments or {}

                if verbose:
                    print(f"[*] Tool Call: {func_name}({func_args})")

                tool_func = TOOL_MAP.get(func_name)
                if tool_func:
                    try:
                        tool_result = str(tool_func(**func_args))
                    except Exception as e:
                        tool_result = f"Error executing tool {func_name}: {str(e)}"
                else:
                    tool_result = f"Error: Tool '{func_name}' is not recognized."

                if verbose:
                    preview = tool_result[:250] + ("..." if len(tool_result) > 250 else "")
                    print(f"[->] Result: {preview}")

                messages.append({
                    "role": "tool",
                    "content": tool_result
                })
        else:
            if verbose:
                print("\n[Agent Completed Task]")
            return response.message.content or "Task completed."

    return "Agent reached maximum iteration limit."

def interactive_coding_agent(model: str = "qwen3:4b"):
    print("=" * 65)
    print("🚀 Local Autonomous Coding Agent")
    print(f"📌 Active Model: {model} (Qwen 3 / Local LLM)")
    print("🛠️ Tools: read_code, write_code, replace_in_file, search_code, run_command")
    print("Type 'exit' to quit.")
    print("=" * 65)

    while True:
        try:
            prompt = input("\nCoding Task > ").strip()
            if not prompt:
                continue
            if prompt.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            result = run_coding_agent(prompt, model=model, verbose=True)
            print("\n" + "=" * 30 + " Agent Response " + "=" * 30)
            print(result)
            print("=" * 76)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Autonomous Local Coding Agent")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Model to use (default: qwen3:4b)")
    parser.add_argument("--task", type=str, help="Coding task to execute non-interactively")

    args = parser.parse_args()
    if args.task:
        output = run_coding_agent(args.task, model=args.model, verbose=True)
        print("\nFinal Output:\n", output)
    else:
        interactive_coding_agent(model=args.model)
