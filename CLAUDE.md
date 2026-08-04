## Python Environment Rules

1. **Virtual Environment Verification:**
   - BEFORE executing any command related to Python or `pip` (e.g., installing packages, running scripts, running CLI tools), ALWAYS check the currently active Python path using `which python` (Linux) or `where.exe python` / `Get-Command python` (Windows).
   - Verify if the output points to the intended `.venv` directory.

2. **Environment Activation Commands:**
   - **Linux / Fish Shell (CachyOS):**
     If `which python` does NOT start with `/home/theone1/.venv/bin/python`, activate it first using:
     ```fish
     source ~/.venv/bin/activate.fish
     ```
   - **Linux / Bash or Zsh:**
     `activate.fish` is fish-only syntax and fails with `parse error near 'end'` in bash/zsh. Use the POSIX script instead:
     ```bash
     source ~/.venv/bin/activate
     ```
   - **Windows:**
     If on Windows and `.venv` is not active, activate using:
     ```powershell
     D:\Documents\code\.venv\Scripts\Activate.ps1
     ```

3. **Execution Execution Standard:**
   - Combine activation and execution in one line if the environment is not pre-activated:
     - Linux (Fish): `source ~/.venv/bin/activate.fish; pip install <package>`
     - Linux (Bash/Zsh): `source ~/.venv/bin/activate && pip install <package>`
     - Windows: `D:\Documents\code\.venv\Scripts\Activate.ps1; pip install <package>`