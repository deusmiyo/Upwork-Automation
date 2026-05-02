import os
import threading
import pandas as pd
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# ── Global scrape state ────────────────────────────────────────────────────────
scrape_status = {
    "running": False,
    "log": [],
    "done": False,
    "error": None,
}
scrape_lock = threading.Lock()


# ── Routes ─────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chart-data")
def chart_data():
    """Read upwork_jobs.xlsx and return skill counts sorted descending."""
    excel_path = os.getenv("EXCEL_PATH", "upwork_jobs.xlsx")
    try:
        df = pd.read_excel(excel_path)
        if "Tagged Skill" not in df.columns:
            return jsonify({"error": "Column 'Tagged Skill' not found in Excel."}), 400

        counts = (
            df["Tagged Skill"]
            .dropna()
            .str.strip()
            .value_counts()
            .sort_values(ascending=True)   # ascending so Plotly renders top → bottom
        )
        return jsonify({
            "skills": counts.index.tolist(),
            "counts": counts.values.tolist(),
        })
    except FileNotFoundError:
        return jsonify({"error": f"Excel file not found: {excel_path}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scrape", methods=["POST"])
def start_scrape():
    """Start the scraper in a background thread."""
    global scrape_status

    with scrape_lock:
        if scrape_status["running"]:
            return jsonify({"error": "A scrape is already running."}), 409

        data = request.get_json(force=True)
        url = (data or {}).get("url", "").strip()
        if not url:
            return jsonify({"error": "No URL provided."}), 400

        scrape_status = {"running": True, "log": [], "done": False, "error": None}

    thread = threading.Thread(target=_run_scrape, args=(url,), daemon=True)
    thread.start()
    return jsonify({"message": "Scrape started."})


@app.route("/api/scrape/status")
def scrape_status_endpoint():
    with scrape_lock:
        return jsonify(dict(scrape_status))


# ── Background worker ──────────────────────────────────────────────────────────
def _run_scrape(url: str):
    """Run the scraper with the supplied URL and stream log lines."""
    import sys
    import io

    global scrape_status

    def _log(msg: str):
        with scrape_lock:
            scrape_status["log"].append(msg)

    try:
        # Patch stdout so print() inside main.py flows into our log
        old_stdout = sys.stdout
        sys.stdout = _LogWriter(_log)

        try:
            # Import the scraping function and override its hard-coded URL
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "scraper_module",
                os.path.join(os.path.dirname(__file__), "main.py"),
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Call scrape with the user-supplied URL
            mod.scrape_upwork_jobs(url)

        finally:
            sys.stdout = old_stdout

    except Exception as exc:
        with scrape_lock:
            scrape_status["error"] = str(exc)
        _log(f"ERROR: {exc}")

    with scrape_lock:
        scrape_status["running"] = False
        scrape_status["done"] = True


class _LogWriter:
    """Redirect print() output to our log list."""

    def __init__(self, log_fn):
        self._log = log_fn
        self._buf = ""

    def write(self, text):
        self._buf += text
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line:
                self._log(line)

    def flush(self):
        pass


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)
