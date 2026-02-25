# AGENTS.md

## Cursor Cloud specific instructions

### Project overview
pip-turbo is a single-file Python CLI tool (`install_requirements.py`) that concurrently installs pip packages from a `requirements.txt` file using `ThreadPoolExecutor`. It uses only Python stdlib — no external dependencies.

### Running the application
```bash
python3 install_requirements.py
```
The script reads `requirements.txt` from the current directory by default. See `README.md` for programmatic usage with custom parameters.

### Linting
No linter config is included in the repo. Use `pyflakes` or `py_compile` for basic checks:
```bash
python3 -m pyflakes install_requirements.py
python3 -m py_compile install_requirements.py
```

### Testing
No automated test suite exists. To manually verify the tool:
1. Create a `requirements.txt` with a few small packages (e.g., `chardet`, `colorama`).
2. Run `python3 install_requirements.py` and verify the concurrent install output.
3. Clean up any generated `requirements_failed.txt` after testing.

### Gotchas
- The `__main__` block hardcodes the path `requirements.txt` — it does not accept CLI arguments. Use the Python API for custom file paths.
- On this environment, pip installs to user site-packages (`~/.local/lib/python3.12/site-packages`) since system site-packages is not writable. This is expected and does not affect functionality.
