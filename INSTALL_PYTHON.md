# Install Python - Quick Guide

## The Issue

The path `C:\Users\91890\AppData\Local\Microsoft\WindowsApps\python.exe` is a **Windows App Execution Alias** (a stub), not an actual Python installation. This is why you're getting the "Python was not found" error.

## Solution: Install Python from Microsoft Store

### Step 1: Install Python from Microsoft Store

1. **Open Microsoft Store:**
   - Press `Windows Key + R`
   - Type: `ms-windows-store://pdp/?ProductId=9NRWMJP3717K`
   - Press Enter
   
   OR
   
   - Open Microsoft Store manually
   - Search for "Python 3.11" or "Python 3.12"
   - Click "Install"

2. **Wait for installation to complete**

### Step 2: Verify Installation

After installation, **close and reopen your terminal**, then run:

```powershell
python --version
pip --version
```

### Step 3: Install Project Dependencies

Once Python is installed, run:

```powershell
pip install -r requirements.txt
```

## Alternative: Install from python.org

If Microsoft Store doesn't work, download from:

1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or 3.12 for Windows
3. **IMPORTANT:** During installation, check "Add Python to PATH"
4. Complete installation
5. Close and reopen terminal
6. Verify: `python --version`

## After Python is Installed

1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Set up secrets:**
   - Copy `streamlit/secrets.toml.example` to `streamlit/secrets.toml`
   - Edit `streamlit/secrets.toml` and add:
     ```toml
     OPENAI_API_KEY = "your-openai-api-key"
     SMTP_USERNAME = "your-email@gmail.com"
     SMTP_PASSWORD = "your-app-password"
     EMAIL_FROM = "your-email@gmail.com"
     ```

3. **Run the app:**
   ```powershell
   streamlit run app/main.py
   ```

## Troubleshooting

### If Python still not found after installation:

1. **Restart your computer** (sometimes needed for PATH updates)

2. **Check if Python is installed:**
   ```powershell
   Get-Command python -ErrorAction SilentlyContinue
   ```

3. **Use full path if needed:**
   - Find actual Python installation (usually in `C:\Users\YourName\AppData\Local\Programs\Python\`)
   - Use: `C:\Users\91890\AppData\Local\Programs\Python\Python3x\python.exe -m pip install -r requirements.txt`

### If you get permission errors:

Run PowerShell as Administrator and try again.

