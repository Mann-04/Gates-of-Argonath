# Setup Guide - Python Installation

## Python is Not Installed

It appears Python is not installed on your system. Follow these steps to install Python:

## Option 1: Install Python from python.org (Recommended)

1. **Download Python:**
   - Go to https://www.python.org/downloads/
   - Download the latest Python 3.11 or 3.12 version for Windows

2. **Install Python:**
   - Run the installer
   - **IMPORTANT:** Check the box "Add Python to PATH" during installation
   - Click "Install Now"

3. **Verify Installation:**
   - Open a new PowerShell/Command Prompt window
   - Run: `python --version`
   - Run: `pip --version`

## Option 2: Install via Microsoft Store

1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.12"
3. Click "Install"
4. After installation, restart your terminal

## Option 3: Install via Chocolatey (if you have it)

```powershell
choco install python
```

## After Python Installation

1. **Close and reopen your terminal** (important for PATH to update)

2. **Verify Python is installed:**
   ```powershell
   python --version
   pip --version
   ```

3. **Install project dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up secrets:**
   - Copy `streamlit/secrets.toml.example` to `streamlit/secrets.toml`
   - Add your OpenAI API key and email credentials

5. **Run the application:**
   ```powershell
   streamlit run app/main.py
   ```

## Troubleshooting

### If `pip` is still not recognized after installing Python:

1. **Use python -m pip instead:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

2. **Check if Python is in PATH:**
   ```powershell
   $env:PATH
   ```
   Look for Python installation path (usually `C:\Python3x\` or `C:\Users\YourName\AppData\Local\Programs\Python\Python3x\`)

3. **Manually add Python to PATH:**
   - Open System Properties → Environment Variables
   - Add Python installation directory to PATH
   - Add `Scripts` folder to PATH (usually `C:\Python3x\Scripts\`)

### If you're using a virtual environment:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Quick Test

After installation, test with:
```powershell
python -c "print('Python is working!')"
```

