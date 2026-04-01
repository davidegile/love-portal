$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python -m PyInstaller --noconfirm --clean love_portal.spec

Write-Host ""
Write-Host "Windows build completed."
Write-Host "Executable output:"
Write-Host "  $root\\dist\\LovePortal.exe"
