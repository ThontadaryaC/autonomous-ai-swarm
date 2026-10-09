import os
import sys
import glob
from pathlib import Path

# Ensure standard output supports UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import ollama

def list_directory(path: str = ".") -> str:
    """Lists files and subdirectories in the specified directory path.
    Args:
        path: The directory path to list (e.g. 'C:\\Users\\cool\\Desktop' or './')
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: Path does not exist: {resolved}"
        if not os.path.isdir(resolved):
            return f"Error: Path is not a directory: {resolved}"
        
        entries = []
        for item in os.scandir(resolved):
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            size = ""
            if item.is_file():
                try:
                    size_bytes = item.stat().st_size
                    if size_bytes < 1024:
                        size = f" ({size_bytes} B)"
                    elif size_bytes < 1024 * 1024:
                        size = f" ({size_bytes / 1024:.1f} KB)"
                    else:
                        size = f" ({size_bytes / (1024 * 1024):.1f} MB)"
                except Exception:
                    pass
            entries.append(f"{item_type} {item.name}{size}")
        
        if not entries:
            return f"Directory {resolved} is empty."
        return f"Contents of {resolved}:\n" + "\n".join(entries)
    except Exception as e:
        return f"Error accessing directory: {str(e)}"

def read_file(path: str, max_lines: int = 200) -> str:
    """Reads content from a file in any location on the system.
    Args:
        path: Full or relative path to the file.
        max_lines: Maximum number of lines to read (default 200).
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: File does not exist: {resolved}"
        if os.path.isdir(resolved):
            return f"Error: Path is a directory, not a file: {resolved}"
        
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            lines = [f.readline() for _ in range(max_lines)]
            content = "".join(lines)
            if f.readline():
                content += f"\n... [Truncated after {max_lines} lines]"
            return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def search_files(directory: str = ".", pattern: str = "*.*", recursive: bool = True) -> str:
    """Searches for files matching a pattern within a directory.
    Args:
        directory: The root directory to start searching from.
        pattern: Wildcard search pattern (e.g. '*.py', '*resume*', '*.json').
        recursive: Whether to search recursively in subfolders (default True).
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(directory))
        if not os.path.exists(resolved):
            return f"Error: Path does not exist: {resolved}"
        
        search_path = os.path.join(resolved, "**", pattern) if recursive else os.path.join(resolved, pattern)
        matches = glob.glob(search_path, recursive=recursive)
        
        if not matches:
            return f"No files matching '{pattern}' found in {resolved}."
        
        result_lines = matches[:50]
        res = f"Found {len(matches)} match(es) for '{pattern}' (showing up to 50):\n" + "\n".join(result_lines)
        if len(matches) > 50:
            res += f"\n... and {len(matches) - 50} more."
        return res
    except Exception as e:
        return f"Error searching files: {str(e)}"

def get_file_info(path: str) -> str:
    """Gets metadata and details about a file or folder.
    Args:
        path: Path to the file or folder.
    """
    try:
        resolved = os.path.expanduser(os.path.expandvars(path))
        if not os.path.exists(resolved):
            return f"Error: Path does not exist: {resolved}"
        
        stat = os.stat(resolved)
        is_dir = os.path.isdir(resolved)
        return (
            f"Path: {resolved}\n"
            f"Type: {'Directory' if is_dir else 'File'}\n"
            f"Size: {stat.st_size} bytes\n"
            f"Modified Time: {stat.st_mtime}\n"
        )
    except Exception as e:
        return f"Error getting file info: {str(e)}"

AVAILABLE_TOOLS = [list_directory, read_file, search_files, get_file_info]
TOOL_MAP = {
    "list_directory": list_directory,
    "read_file": read_file,
    "search_files": search_files,
    "get_file_info": get_file_info
}

def ask_ollama(prompt: str, model: str = "llama3.2:latest", conversation_history: list = None, verbose: bool = True) -> str:
    if conversation_history is None:
        conversation_history = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant with real-time access to the user's local filesystem. "
                    "You have tools to list directories, read files, search for files, and check file info. "
                    "Always use these tools to inspect real folders and files when the user asks."
                )
            }
        ]
    
    conversation_history.append({"role": "user", "content": prompt})

    max_turns = 10
    turn = 0
    while turn < max_turns:
        turn += 1
        response = ollama.chat(
            model=model,
            messages=conversation_history,
            tools=AVAILABLE_TOOLS
        )

        conversation_history.append(response.message)

        if response.message.tool_calls:
            for tool_call in response.message.tool_calls:
                func_name = tool_call.function.name
                func_args = tool_call.function.arguments or {}
                
                if verbose:
                    print(f"[*] Calling tool: {func_name}({func_args})")
                
                tool_func = TOOL_MAP.get(func_name)
                if tool_func:
                    try:
                        tool_result = str(tool_func(**func_args))
                    except Exception as e:
                        tool_result = f"Error executing tool {func_name}: {str(e)}"
                else:
                    tool_result = f"Error: Tool {func_name} not found."
                
                conversation_history.append({
                    "role": "tool",
                    "content": tool_result
                })
        else:
            return response.message.content

    return "Reached maximum tool execution turns."

def interactive_cli(model: str = "llama3.2:latest"):
    print("=" * 60)
    print("Local LLM File System Assistant")
    print(f"Active Model: {model}")
    print("Skills: list_directory, read_file, search_files, get_file_info")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 60)

    history = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant with real-time access to the user's local filesystem. "
                "You have tools to list directories, read files, search for files, and check file info. "
                "Always use these tools to inspect real folders and files when the user asks."
            )
        }
    ]

    while True:
        try:
            user_input = input("\nYou > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            reply = ask_ollama(user_input, model=model, conversation_history=history, verbose=True)
            print(f"\nAssistant > {reply}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ollama Local File System Assistant")
    parser.add_argument("--model", type=str, default="llama3.2:latest", help="Ollama model to use (e.g. llama3.2:latest, qwen3:4b, gemma3:4b-it-q4_K_M)")
    parser.add_argument("--ask", type=str, help="Single question to ask the model")
    
    args = parser.parse_args()
    if args.ask:
        answer = ask_ollama(args.ask, model=args.model, verbose=True)
        print("\nAnswer:")
        print(answer)
    else:
        interactive_cli(model=args.model)
