---
name: terminal-file-manager
description: Grants all local LLMs (Qwen 3, Gemma 3, Llama 3.2) an always-available terminal connection to create directories, generate files, move/rename assets, and execute shell commands anywhere on the machine.
---

# 💻 Direct Terminal & File System Manager

Equips any local LLM with direct access to your Windows terminal/PowerShell and filesystem.

---

## 🛠️ Built-in Capabilities
1. **`create_directory(path)`**: Creates folders or full nested project directory trees anywhere on your disk.
2. **`create_file(path, content)`**: Creates files anywhere on the system and automatically generates parent directories.
3. **`delete_path(path)`**: Safely removes files or recursively deletes directories.
4. **`move_or_rename(source, destination)`**: Moves or renames files and folders.
5. **`run_terminal(command, cwd)`**: Runs any terminal or PowerShell command with working directory control and returns real STDOUT/STDERR output.

---

## 🚀 How to Run

### 1. Interactive Terminal Assistant (Works with any model)
```powershell
python c:\Users\cool\Desktop\skills\terminal_manager.py --model qwen3:4b
```

### 2. Single Command / Folder Creation
```powershell
python c:\Users\cool\Desktop\skills\terminal_manager.py --ask "Create a new project folder C:\Users\cool\Desktop\my_test_app with src, tests, and docs folders and a README.md file inside"
```

### 3. Switch between models
```powershell
# Using Llama 3.2
python c:\Users\cool\Desktop\skills\terminal_manager.py --model llama3.2:latest --ask "Check git status and create a build folder"

# Using Gemma 3
python c:\Users\cool\Desktop\skills\terminal_manager.py --model gemma3:4b-it-q4_K_M --ask "Create an assets folder with images and css subfolders"
```
