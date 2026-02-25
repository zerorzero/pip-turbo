<div align="center">

# 🚀 pip-turbo

**Install Python packages up to 4x faster.**

[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-42%20passed-brightgreen)](#-testing)
[![No Dependencies](https://img.shields.io/badge/dependencies-0-orange)](#)

pip-turbo reads your `requirements.txt` and installs every package **concurrently** using Python's built-in thread pool — no extra dependencies, no config, just speed.

</div>

---

## ⚡ Benchmark

```
────────────────────────────────────────────────────
  Method                           Time   Speedup
────────────────────────────────────────────────────
  pip install (sequential)        4.02s     1.00x
  pip-turbo   (concurrent)        1.02s      3.9x
────────────────────────────────────────────────────

  pip-turbo is 3.9x faster! 🚀
```

> Measured on 8 packages (`six`, `colorama`, `chardet`, `certifi`, `idna`, `pytz`, `pep8`, `toml`).  
> Run `python benchmark.py` to reproduce on your machine.

## 📋 How It Works

```
requirements.txt          pip-turbo               result
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  requests    │     │  Thread 1 ──▶   │     │ ✅ requests  │
│  pandas      │────▶│  Thread 2 ──▶   │────▶│ ✅ pandas    │
│  numpy       │     │  Thread 3 ──▶   │     │ ✅ numpy     │
│  flask       │     │  Thread 4 ──▶   │     │ ✅ flask     │
└──────────────┘     └─────────────────┘     └──────────────┘
                      4 concurrent threads
```

Instead of installing packages one-by-one, pip-turbo dispatches all of them across a thread pool. Each thread runs its own `pip install` subprocess, so downloads and installs happen in parallel.

## 🛠️ Quick Start

```bash
git clone https://github.com/zerorzero/pip-turbo.git
cd pip-turbo

# run it
python install_requirements.py
```

That's it. No `pip install`, no virtualenv, no setup — it's a single file using only the standard library.

## 🎯 Usage

### CLI

```bash
python install_requirements.py
```

Reads `requirements.txt` from the current directory and installs everything concurrently.

### As a Library

```python
from install_requirements import install_requirements

# Basic — uses sensible defaults
install_requirements('requirements.txt')

# Advanced — tune concurrency, encoding, failure output
install_requirements(
    file_path='requirements.txt',
    encoding='utf-8',
    max_workers=8,
    failed_output='failed.txt'
)
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `file_path` | `'requirements.txt'` | Path to your requirements file |
| `encoding` | `'utf-8'` | File encoding |
| `max_workers` | `4` | Number of concurrent install threads |
| `failed_output` | `'requirements_failed.txt'` | Where to write failed package names |

## 📝 Example Output

```
Starting installation of 5 packages...

✅ Successfully installed: requests
✅ Successfully installed: flask
✅ Successfully installed: numpy
❌ Failed to install: nonexistent-pkg
   Error: Command '[pip, install, nonexistent-pkg]' returned non-zero exit status 1
✅ Successfully installed: pandas

Installation Summary:
✅ Successfully installed: 4
❌ Failed to install: 1

❌ Failed packages have been written to `requirements_failed.txt`.
```

## 🔒 Security

pip-turbo validates every package name against a strict regex before passing it to `pip`, blocking shell injection attempts like:

```
; rm -rf /           → ❌ rejected
&& curl evil.com     → ❌ rejected
$(whoami)            → ❌ rejected
requests>=2.0        → ✅ allowed
flask[async]         → ✅ allowed
```

## 🧪 Testing

The project includes a comprehensive test suite with **42 tests** covering validation, installation mocking, concurrency, error handling, and a live smoke test.

```bash
# run all tests
python -m pytest test_install_requirements.py -v

# skip live (network) tests
python -m pytest test_install_requirements.py -v -m "not live"

# run the benchmark
python benchmark.py
```

## 🌍 Cross-Platform

Works on **Windows**, **macOS**, and **Linux** with automatic pip executable detection and fallback.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Run the tests (`python -m pytest test_install_requirements.py -v`)
4. Commit and push
5. Open a Pull Request

## 📄 License

[MIT](LICENSE) — use it however you want.

---

<div align="center">

**If pip-turbo saved you time, consider giving it a ⭐**

</div>
