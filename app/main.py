from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import Response
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.state import ExperienceState
from app.vision import VisionService

BASE_DIR = Path(__file__).resolve().parent

state = ExperienceState()
vision = VisionService(
    on_detected=state.open_portal,
    on_status=state.update_vision_status,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    vision.start()
    yield
    vision.stop()


app = FastAPI(title="Love Portal", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


class PinPayload(BaseModel):
    pin: str


class PhrasePayload(BaseModel):
    transcript: str
    supported: bool = True


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"page_title": "Love Portal"},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/state")
def get_state() -> dict[str, object]:
    snapshot = state.snapshot()
    return snapshot.__dict__


@app.post("/api/phrase/heard")
def phrase_heard(payload: PhrasePayload) -> dict[str, object]:
    state.update_transcript(payload.transcript, supported=payload.supported)
    matched = state.hear_phrase(payload.transcript)
    snapshot = state.snapshot()
    return {
        "matched": matched,
        "phase": snapshot.phase,
        "status_message": snapshot.status_message,
        "live_transcript": snapshot.live_transcript,
        "heard_phrase": snapshot.heard_phrase,
    }


@app.post("/api/pin/verify")
def verify_pin(payload: PinPayload) -> dict[str, object]:
    ok, message = state.submit_pin(payload.pin)
    snapshot = state.snapshot()
    return {
        "ok": ok,
        "message": message,
        "phase": snapshot.phase,
        "hint": snapshot.hint,
        "pin_attempts": snapshot.pin_attempts,
    }


@app.post("/api/experience/reset")
def reset_experience() -> dict[str, str]:
    state.reset()
    vision.stop()
    vision.start()
    return {"status": "reset"}


@app.get("/video-frame")
def video_frame() -> Response:
    frame = vision.latest_frame()
    if frame is None:
        raise HTTPException(status_code=503, detail="Video frame not ready.")
    return Response(content=frame, media_type="image/jpeg")


def _mjpeg_stream():
    import time

    while True:
        frame = vision.latest_frame()
        if frame is None:
            time.sleep(0.1)
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )
        time.sleep(0.08)


@app.get("/video-feed")
def video_feed() -> StreamingResponse:
    return StreamingResponse(
        _mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
