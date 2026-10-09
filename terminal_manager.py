import os
import sys
import shutil
import subprocess
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ollama

# ==============================================================================
# Always-Available Terminal & Folder/File Operations Toolset
# ==============================================================================

def create_directory(path: str) -> str:
    """Creates a new folder or nested directory structure anywhere on the system.
    Args:
        path: Absolute or relative directory path to create (e.g. 'C:\\Users\\cool\\Desktop\\my_new_project\\src\\components')
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        os.makedirs(resolved, exist_ok=True)
        return f"Successfully created directory: {resolved}"
    except Exception as e:
        return f"Error creating directory '{path}': {str(e)}"

def create_file(path: str, content: str = "") -> str:
    """Creates a new file anywhere on the system, creating parent folders automatically.
    Args:
        path: Path where the file should be created.
        content: Text content to write into the file (optional).
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        os.makedirs(os.path.dirname(os.path.abspath(resolved)), exist_ok=True)
        with open(resolved, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully created file: {resolved} ({len(content)} characters written)"
    except Exception as e:
        return f"Error creating file '{path}': {str(e)}"

def delete_path(path: str) -> str:
    """Deletes a file or directory on the system.
    Args:
        path: Path to the file or directory to remove.
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: Path '{resolved}' does not exist."
        if os.path.isdir(resolved):
            shutil.rmtree(resolved)
            return f"Successfully removed directory: {resolved}"
        else:
            os.remove(resolved)
            return f"Successfully deleted file: {resolved}"
    except Exception as e:
        return f"Error deleting '{path}': {str(e)}"

def move_or_rename(source: str, destination: str) -> str:
    """Moves or renames a file or folder from source to destination.
    Args:
        source: Current path.
        destination: New path.
    """
    try:
        src = os.path.expanduser(os.path.expandvars(source))
        dst = os.path.expanduser(os.path.expandvars(destination))
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        shutil.move(src, dst)
        return f"Successfully moved/renamed '{src}' to '{dst}'"
    except Exception as e:
        return f"Error moving '{source}' to '{destination}': {str(e)}"

def run_terminal(command: str, cwd: str = ".") -> str:
    """Executes any terminal / PowerShell command in a specified directory.
    Args:
        command: Terminal command to run (e.g. 'mkdir project', 'git init', 'npm install', 'python script.py').
        cwd: Working directory to run the command in (default: current directory).
    """
    try:
        working_dir = os.path.expanduser(os.path.expandvars(cwd))
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir if os.path.exists(working_dir) else None,
            timeout=45
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        code = result.returncode

        output = f"Command: {command}\nExit Code: {code}\n"
        if out:
            output += f"STDOUT:\n{out}\n"
        if err:
            output += f"STDERR:\n{err}\n"
        if not out and not err:
            output += "(Command executed successfully with no output)"
        return output
    except subprocess.TimeoutExpired:
        return f"Error: Command '{command}' timed out after 45 seconds."
    except Exception as e:
        return f"Error executing terminal command: {str(e)}"

TERMINAL_TOOLS = [create_directory, create_file, delete_path, move_or_rename, run_terminal]
TOOL_MAP = {
    "create_directory": create_directory,
    "create_file": create_file,
    "delete_path": delete_path,
    "move_or_rename": move_or_rename,
    "run_terminal": run_terminal
}

def ask_terminal_agent(prompt: str, model: str = "qwen3:4b") -> str:
    messages = [
        {
            "role": "system",
            "content": (
                "You are an expert Terminal and System Operations Assistant. "
                "You have direct terminal connection and system access to create directories, create files, "
                "delete paths, move/rename files, and execute PowerShell/terminal commands anytime anywhere. "
                "Always use your tools directly to perform the requested terminal operations."
            )
        },
        {"role": "user", "content": prompt}
    ]

    max_turns = 10
    turn = 0
    while turn < max_turns:
        turn += 1
        try:
            response = ollama.chat(
                model=model,
                messages=messages,
                tools=TERMINAL_TOOLS
            )
        except Exception as e:
            return f"Error: {str(e)}"

        messages.append(response.message)

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                name = tool_call.function.name
                args = tool_call.function.arguments or {}
                print(f"[*] Terminal Tool: {name}({args})")
                func = TOOL_MAP.get(name)
                if func:
                    try:
                        res = str(func(**args))
                    except Exception as e:
                        res = f"Error: {str(e)}"
                else:
                    res = f"Error: Tool {name} not found."
                messages.append({"role": "tool", "content": res})
        else:
            return response.message.content or "Completed."

    return "Max turns reached."

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Terminal & File System Operations Engine")
    parser.add_argument("--model", type=str, default="qwen3:4b", help="Model to use (qwen3:4b, gemma3:4b-it-q4_K_M, llama3.2:latest)")
    parser.add_argument("--ask", type=str, help="Instruction to execute via terminal")

    args = parser.parse_args()
    if args.ask:
        ans = ask_terminal_agent(args.ask, model=args.model)
        print("\nResult:\n", ans)
    else:
        print("=" * 65)
        print(f"💻 Direct Terminal & File System Engine ({args.model})")
        print("Tools: create_directory, create_file, delete_path, move_or_rename, run_terminal")
        print("Type 'exit' to quit.")
        print("=" * 65)
        while True:
            try:
                user_in = input("\nTerminal Agent > ").strip()
                if not user_in:
                    continue
                if user_in.lower() in ["exit", "quit"]:
                    break
                print("\nAssistant >", ask_terminal_agent(user_in, model=args.model))
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
