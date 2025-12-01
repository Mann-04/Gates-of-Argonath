# Script to find Python and install dependencies

Write-Host "Searching for Python installation..." -ForegroundColor Yellow

# Common Python installation paths
$pythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
    "$env:PROGRAMFILES\Python*\python.exe",
    "$env:PROGRAMFILES(X86)\Python*\python.exe",
    "C:\Python*\python.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Python\Python*\python.exe"
)

$foundPython = $null

# Search for Python
foreach ($path in $pythonPaths) {
    $matches = Get-ChildItem -Path $path -ErrorAction SilentlyContinue
    if ($matches) {
        foreach ($match in $matches) {
            try {
                $version = & $match.FullName --version 2>&1
                if ($LASTEXITCODE -eq 0 -and $version -notlike "*was not found*") {
                    $foundPython = $match.FullName
                    Write-Host "Found Python at: $foundPython" -ForegroundColor Green
                    Write-Host "Version: $version" -ForegroundColor Green
                    break
                }
            } catch {
                continue
            }
        }
        if ($foundPython) { break }
    }
}

# If not found, try to use python command
if (-not $foundPython) {
    Write-Host "Trying 'python' command..." -ForegroundColor Yellow
    try {
        $version = python --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $version -notlike "*was not found*" -and $version -notlike "*install from*") {
            $foundPython = "python"
            Write-Host "Found Python: $version" -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not find Python using 'python' command" -ForegroundColor Red
    }
}

# If still not found, ask user
if (-not $foundPython) {
    Write-Host "`nPython not found automatically." -ForegroundColor Red
    Write-Host "Please provide the full path to your Python executable." -ForegroundColor Yellow
    Write-Host "Example: C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe" -ForegroundColor Cyan
    $userPath = Read-Host "Enter Python path (or press Enter to exit)"
    
    if ($userPath -and (Test-Path $userPath)) {
        $foundPython = $userPath
        Write-Host "Using Python at: $foundPython" -ForegroundColor Green
    } else {
        Write-Host "Invalid path or cancelled. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Install dependencies
Write-Host "`nInstalling dependencies from requirements.txt..." -ForegroundColor Yellow

try {
    if ($foundPython -eq "python") {
        & python -m pip install --upgrade pip
        & python -m pip install -r requirements.txt
    } else {
        & $foundPython -m pip install --upgrade pip
        & $foundPython -m pip install -r requirements.txt
    }
    
    Write-Host "`nDependencies installed successfully!" -ForegroundColor Green
    Write-Host "You can now run the app with: streamlit run app/main.py" -ForegroundColor Cyan
} catch {
    Write-Host "Error installing dependencies: $_" -ForegroundColor Red
    exit 1
}

