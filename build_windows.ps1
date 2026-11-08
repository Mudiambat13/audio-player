$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    throw "Environnement introuvable. Créez-le avec : python -m venv .venv"
}

$Python = ".\.venv\Scripts\python.exe"
& $Python -m pip install -r requirements-build.txt
if ($LASTEXITCODE -ne 0) {
    throw "Installation des dépendances de compilation impossible."
}

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name Jonathan `
    --add-data "assets;assets" `
    main.py
if ($LASTEXITCODE -ne 0) {
    throw "La création de Jonathan.exe a échoué."
}

Write-Host "Application prête : $PSScriptRoot\dist\Jonathan\Jonathan.exe"
