from __future__ import annotations

import socket
import threading
import time
import webbrowser
from urllib.request import urlopen

import uvicorn

try:
    import webview  # type: ignore
except ImportError:  # pragma: no cover
    webview = None


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(url: str, timeout_seconds: float = 15.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urlopen(url, timeout=1.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise TimeoutError(f"Server did not become ready: {url}")


def _run_server(port: int) -> uvicorn.Server:
    config = uvicorn.Config(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    server_thread = threading.Thread(target=server.run, daemon=True, name="love-portal-server")
    server_thread.start()
    return server


def _run_native_window(url: str) -> bool:
    if webview is None:
        return False

    window = webview.create_window(
        "Love Portal",
        url,
        fullscreen=True,
        text_select=True,
        background_color="#120f14",
    )
    webview.start()
    return window is not None


def main() -> None:
    port = _pick_free_port()
    url = f"http://127.0.0.1:{port}/health"
    app_url = f"http://127.0.0.1:{port}"
    server = _run_server(port)
    _wait_for_server(url)

    try:
        if not _run_native_window(app_url):
            webbrowser.open(app_url)
            while not server.should_exit:
                time.sleep(0.5)
    except KeyboardInterrupt:  # pragma: no cover
        server.should_exit = True
    finally:
        server.should_exit = True


if __name__ == "__main__":
    main()
