from __future__ import annotations

import socket
import threading
import time
import webbrowser
from dataclasses import dataclass
from urllib.request import urlopen

import uvicorn

try:
    import webview  # type: ignore
except ImportError:  # pragma: no cover
    webview = None


@dataclass
class ServerRuntime:
    server: uvicorn.Server
    thread: threading.Thread
    startup_error: list[BaseException]


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_server(runtime: ServerRuntime, url: str, timeout_seconds: float = 60.0) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if runtime.startup_error:
            raise RuntimeError("Embedded server crashed during startup.") from runtime.startup_error[0]
        if not runtime.thread.is_alive() and not runtime.server.started:
            raise RuntimeError("Embedded server stopped before becoming ready.")
        try:
            with urlopen(url, timeout=1.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.2)
    raise TimeoutError(f"Server did not become ready: {url}")


def _load_app():
    from app.main import app

    return app


def _run_server(port: int) -> ServerRuntime:
    startup_error: list[BaseException] = []
    config = uvicorn.Config(
        _load_app(),
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)

    def server_target() -> None:
        try:
            server.run()
        except BaseException as exc:  # pragma: no cover
            startup_error.append(exc)
            raise

    server_thread = threading.Thread(target=server_target, daemon=True, name="love-portal-server")
    server_thread.start()
    return ServerRuntime(server=server, thread=server_thread, startup_error=startup_error)


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
    runtime = _run_server(port)
    _wait_for_server(runtime, url)

    try:
        if not _run_native_window(app_url):
            webbrowser.open(app_url)
            while not runtime.server.should_exit:
                time.sleep(0.5)
    except KeyboardInterrupt:  # pragma: no cover
        runtime.server.should_exit = True
    finally:
        runtime.server.should_exit = True


if __name__ == "__main__":
    main()
