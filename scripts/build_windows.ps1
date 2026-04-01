$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (Test-Path "$root\dist\LovePortal.exe") {
    try {
        Remove-Item -LiteralPath "$root\dist\LovePortal.exe" -Force
    } catch {
        throw "Chiudi LovePortal.exe prima di rigenerare la build Windows."
    }
}

python -m PyInstaller --noconfirm --clean love_portal.spec

Write-Host ""
Write-Host "Windows build completed."
Write-Host "Executable output:"
Write-Host "  $root\\dist\\LovePortal.exe"
