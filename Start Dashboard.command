#!/bin/bash

# Navigate to the folder where this script is located
cd "$(dirname "$0")"

# ── Check for Python 3 ────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    # Show a native Mac popup error
    osascript -e 'display alert "Python 3 is missing" message "Please install Python 3 from python.org. After installing, try opening the Dashboard again."'
    open "https://www.python.org/downloads/"
    exit 1
fi

# ── Check for Google Chrome ───────────────────────────────────────────────────
if [ ! -d "/Applications/Google Chrome.app" ] && [ ! -d "$HOME/Applications/Google Chrome.app" ]; then
    osascript -e 'display alert "Google Chrome is missing" message "Google Chrome must be installed to run this scraper. Please download and install it."'
    open "https://www.google.com/chrome/"
    exit 1
fi

# ── Launch the app silently in the background ─────────────────────────────────
nohup python3 launcher.py > /dev/null 2>&1 &

# ── Close the Terminal window that popped up ──────────────────────────────────
osascript -e 'tell application "Terminal" to close first window' &
exit 0
