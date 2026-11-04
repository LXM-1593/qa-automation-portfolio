# Run the UI regression suite on Windows.
# Usage: powershell -ExecutionPolicy Bypass -File scripts/run_tests.ps1 [-m smoke]
param(
    [string]$PytestArgs = ""
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# ChromeDriver talks to Chrome over localhost; keep that traffic out of any proxy.
$env:NO_PROXY = "localhost,127.0.0.1,::1"

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run: python -m venv .venv && .venv\Scripts\python.exe -m pip install -r requirements.txt"
}

if ($PytestArgs) {
    & $python -m pytest $PytestArgs.Split(" ")
} else {
    & $python -m pytest
}
exit $LASTEXITCODE
