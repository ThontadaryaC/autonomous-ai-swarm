---
name: coding-agent
description: Autonomous coding agent for local LLMs (Qwen 3, Llama 3.2, Gemma 3) with code inspection, file editing, search, and terminal test execution.
---

# Autonomous Coding Agent Skill

This skill equips local LLMs (especially `qwen3:4b`) to act as an autonomous coding assistant capable of creating code, editing existing projects, running commands/tests, and debugging errors automatically.

## Capabilities & Tools
1. **`read_code_file(path, start_line, end_line)`**: Inspects code with numbered lines.
2. **`write_code_file(path, content)`**: Creates new source files or overwrites existing ones.
3. **`replace_in_file(path, target_code, replacement_code)`**: Performs precise code modifications.
4. **`search_codebase(directory, keyword)`**: Finds function definitions, classes, or imports across projects.
5. **`run_command(command)`**: Executes terminal commands (e.g., `pytest`, `python script.py`, `npm test`) to verify code.

## How to Use
- **Interactive Mode**:
  ```powershell
  python c:\Users\cool\Desktop\skills\coding_agent.py --model qwen3:4b
  ```

- **One-off Coding Task**:
  ```powershell
  python c:\Users\cool\Desktop\skills\coding_agent.py --model qwen3:4b --task "Write a script in this folder that converts markdown files to HTML and test it"
  ```
