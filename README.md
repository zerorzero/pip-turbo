# 🚀 pip-turbo

A fast, concurrent Python package installer that supercharges your pip installations using multi-threading.

## ✨ Features

- **Concurrent Installation**: Installs multiple packages simultaneously using thread pooling
- **Progress Tracking**: Real-time installation status with clear success/failure indicators
- **Failed Package Logging**: Automatically saves failed installations to a separate requirements file
- **Simple to Use**: Works with standard requirements.txt files
- **Error Handling**: Robust error handling with detailed failure reporting

## 🛠️ Installation

Clone the repository:
```bash
git clone https://github.com/zerorzero/pip-turbo.git
cd pip-turbo
```


## 📋 Usage

1. Basic usage with default settings:

```bash
python install_requirements.py
```


2. Import and use in your Python code:

```python
from install_requirements import install_requirements

# Basic usage
install_requirements('requirements.txt')

# Advanced usage with custom parameters
install_requirements(
file_path='requirements.txt',
encoding='utf-8',
max_workers=4,
failed_output='requirements_failed.txt'
)
```


## ⚙️ Parameters

- `file_path`: Path to your requirements file (default: 'requirements.txt')
- `encoding`: File encoding (default: 'utf-8')
- `max_workers`: Number of concurrent installation threads (default: 4)
- `failed_output`: Output file for failed installations (default: 'requirements_failed.txt')

## 📝 Output Example

Starting installation of 10 packages...   
✅ Successfully installed: requests  
✅ Successfully installed: pandas  
❌ Failed to install: non-existent-package  
Error: Command '[pip, install, non-existent-package]' returned non-zero exit status 1  
✅ Successfully installed: numpy  
Installation Summary:  
✅ Successfully installed: 3  
❌ Failed to install: 1  
❌ Failed packages have been written to requirements_failed.txt.  


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Note

This tool requires Python 3.6+ and runs on Windows systems (uses Windows-specific pip path). For other operating systems, minor modifications may be needed.

