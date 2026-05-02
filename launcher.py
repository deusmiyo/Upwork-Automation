"""
launcher.py — Upwork Dashboard system-tray launcher.

Run this file (via Start Dashboard.bat or directly with pythonw).
It will:
  1. Silently start the Flask server in a background thread.
  2. Auto-open the dashboard in the default browser.
  3. Place an icon in the Windows system tray with Open / Quit options.
"""

import os
import sys
import time
import threading
import webbrowser
import subprocess

# ── Make sure we run from the directory this file lives in ────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

# ── Dependency check / silent install ─────────────────────────────────────────
def _ensure_deps():
    req = os.path.join(BASE_DIR, "requirements.txt")
    log_file = os.path.join(BASE_DIR, "install_log.txt")
    
    # Try to install setuptools first as it is required for distutils shims in Python 3.12+
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "setuptools", "-q"])
    except:
        pass

    if not os.path.exists(req):
        return
        
    try:
        with open(log_file, "w") as f:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-r", req, "-q", "--exists-action", "i"],
                stdout=f,
                stderr=f,
            )
    except Exception:
        pass  # Flask will fail later if critical deps are missing

_ensure_deps()

# ── Now safe to import third-party packages ───────────────────────────────────
from PIL import Image, ImageDraw
import pystray

PORT = int(os.environ.get("PORT", 5000))
DASHBOARD_URL = f"http://127.0.0.1:{PORT}"

# ── Build a simple tray icon (purple circle with "U") ─────────────────────────
def _make_icon() -> Image.Image:
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Purple filled circle
    draw.ellipse([2, 2, size - 2, size - 2], fill=(108, 99, 255, 255))
    # White "U" — drawn as two vertical bars + bottom arc approximation
    m = size // 2
    bar_w = 6
    bar_h = 28
    gap = 10
    draw.rectangle([m - gap - bar_w, 12, m - gap, 12 + bar_h], fill="white")
    draw.rectangle([m + gap, 12, m + gap + bar_w, 12 + bar_h], fill="white")
    draw.ellipse([m - gap - bar_w, 12 + bar_h - bar_w, m + gap + bar_w, 12 + bar_h + bar_w + 4], fill="white")
    return img


# ── Flask server thread ────────────────────────────────────────────────────────
_flask_started = threading.Event()

def _run_flask():
    # Suppress Flask's startup banner
    import logging
    log = logging.getLogger("werkzeug")
    log.setLevel(logging.ERROR)

    from app import app
    from dotenv import load_dotenv
    load_dotenv()

    _flask_started.set()
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

flask_thread = threading.Thread(target=_run_flask, daemon=True)
flask_thread.start()

# Wait for Flask to be ready (up to 10 s), then open the browser
def _open_browser():
    _flask_started.wait(timeout=10)
    time.sleep(0.6)  # small grace period for the first request
    webbrowser.open(DASHBOARD_URL)

threading.Thread(target=_open_browser, daemon=True).start()


# ── Tray icon setup ────────────────────────────────────────────────────────────
def _on_open(icon, item):
    webbrowser.open(DASHBOARD_URL)

def _on_quit(icon, item):
    icon.stop()
    os._exit(0)  # hard-exit kills Flask thread too

menu = pystray.Menu(
    pystray.MenuItem("Open Dashboard", _on_open, default=True),
    pystray.Menu.SEPARATOR,
    pystray.MenuItem("Quit", _on_quit),
)

tray = pystray.Icon(
    name="Upwork Dashboard",
    icon=_make_icon(),
    title="Upwork Dashboard",
    menu=menu,
)

tray.run()
