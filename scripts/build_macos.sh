#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python -m PyInstaller --noconfirm --clean love_portal.spec

APP_PATH="$ROOT/dist/LovePortal.app"
DMG_PATH="$ROOT/dist/LovePortal.dmg"

rm -f "$DMG_PATH"
hdiutil create -volname "LovePortal" -srcfolder "$APP_PATH" -ov -format UDZO "$DMG_PATH"

echo ""
echo "macOS build completed."
echo "App bundle: $APP_PATH"
echo "DMG package: $DMG_PATH"
