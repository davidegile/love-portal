# Packaging

## Goal
Distribuire l'app senza richiedere all'utente finale l'installazione di Python o dipendenze.

## Output targets
- Windows: `LovePortal.exe`
- macOS: `LovePortal.app`
- macOS distributable: `LovePortal.dmg`

## Build prerequisites
I prerequisiti valgono solo per la macchina di build:
- Python virtual environment attivo
- dipendenze installate con `pip install -e .[dev]`
- su macOS, `hdiutil` disponibile nel sistema

## Windows build
```powershell
./scripts/build_windows.ps1
```

Output atteso:
- `dist/LovePortal.exe`

## macOS build
```bash
./scripts/build_macos.sh
```

Output atteso:
- `dist/LovePortal.app`
- `dist/LovePortal.dmg`

## Runtime behavior
- Il launcher standalone avvia il server locale Uvicorn
- prova prima ad aprire una finestra desktop nativa full-screen con `pywebview`
- in fallback apre il browser predefinito sulla porta locale scelta automaticamente
- l'utente usa l'app senza installare altro

## Current limitations
- Le build devono essere prodotte sulla piattaforma target
- Il packaging reale di OpenCV e MediaPipe va validato su Windows e macOS
- La firma del codice macOS non e' ancora configurata
