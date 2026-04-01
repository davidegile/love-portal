# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

project_root = Path(SPECPATH)

datas = [
    (str(project_root / "app" / "static"), "app/static"),
    (str(project_root / "app" / "templates"), "app/templates"),
]

hiddenimports = [
    "uvicorn.logging",
    "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets.auto",
    "jinja2",
    "cv2",
    "mediapipe",
    "webview",
]

a = Analysis(
    ["app/launcher.py"],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="LovePortal",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

app = BUNDLE(
    exe,
    name="LovePortal.app",
    icon=None,
    bundle_identifier="com.david.loveportal",
)
