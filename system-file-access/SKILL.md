---
name: system-file-access
description: Enables local Ollama LLMs (Llama 3.2, Qwen 3, Gemma 3) to browse directories, search for files, inspect metadata, and read project files from anywhere on the system.
---

# System File Access Skill for Local LLMs

This skill equips local LLM models running via Ollama with full filesystem access via tool calling.

## Available Capabilities
1. **`list_directory(path)`**: Lists all subfolders and files with file sizes.
2. **`read_file(path, max_lines)`**: Reads file contents from any project or text file across the system.
3. **`search_files(directory, pattern)`**: Performs recursive file searches using glob patterns (e.g. `*.py`, `*report*`, `*.json`).
4. **`get_file_info(path)`**: Returns file size, type, and modified timestamps.

## How to Run
- **Interactive Chat**:
  ```powershell
  python c:\Users\cool\Desktop\skills\ask_ollama.py
  ```
- **Single Question**:
  ```powershell
  python c:\Users\cool\Desktop\skills\ask_ollama.py --ask "Show me what files are in C:\Users\cool\Desktop"
  ```
- **Choose Specific Model**:
  ```powershell
  python c:\Users\cool\Desktop\skills\ask_ollama.py --model qwen3:4b --ask "List the folders in C:\Users\cool"
  ```
