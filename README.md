# Love Portal

Esperienza locale in Python che usa la webcam per rilevare un cuore con le mani, aprire un portale virtuale full-screen, richiedere il PIN `2805` e mostrare una lettera finale.

## Stack
- Python 3.12+
- FastAPI
- Uvicorn
- OpenCV
- MediaPipe
- Jinja2
- Frontend HTML/CSS/JavaScript locale

## Avvio previsto
1. Creare un virtual environment Python.
2. Installare le dipendenze con `pip install -e .[dev]`.
3. Avviare il server con `uvicorn app.main:app --reload`.
4. Aprire `http://127.0.0.1:8000` e premere `Inizia` per entrare in full-screen.

## Packaging
- Windows standalone: `./scripts/build_windows.ps1`
- macOS standalone: `./scripts/build_macos.sh`
- Dettagli in `PACKAGING.md`
- Output Windows corrente: `dist/LovePortal.exe`

## Stato
MVP verticale disponibile: stato esperienza, portale, PIN con suggerimenti progressivi, lettera placeholder e base di gesture detection con MediaPipe/OpenCV.
