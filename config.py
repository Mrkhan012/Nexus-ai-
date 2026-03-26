"""
config.py — Nexus Configuration
Edit the paths below to match the apps installed on YOUR computer.
"""

import os

# ─── BASE DIRECTORIES ─────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR  = os.path.join(BASE_DIR, "storage")         # Where Nexus saves files
MODEL_PATH   = os.path.join(BASE_DIR, "model", "nexus_model.pkl")
DB_PATH      = os.path.join(BASE_DIR, "model", "nexus_memory.db")

# ─── APPLICATION PATHS (Windows) ──────────────────────────────────────────────
APPS = {
    "notepad"     : r"C:\Windows\System32\notepad.exe",
    "calculator"  : r"C:\Windows\System32\calc.exe",
    "paint"       : r"C:\Windows\System32\mspaint.exe",
    "cmd"         : r"C:\Windows\System32\cmd.exe",
    "explorer"    : r"C:\Windows\explorer.exe",

    # Browsers (update path if Chrome is installed elsewhere)
    "chrome"      : r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "edge"        : r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    # Dev tools (update to your actual install paths)
    "vscode"      : r"C:\Users\PATHAN\AppData\Local\Programs\Microsoft VS Code\Code.exe",

    # Office
    "excel"       : r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "word"        : r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "powerpoint"  : r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",

    # Common Web-Links / Apps
    "youtube"     : "https://www.youtube.com",
    "google"      : "https://www.google.com",
    "spotify"     : "spotify",

    # Photoshop (update if installed)
    "photoshop"   : r"C:\Program Files\Adobe\Adobe Photoshop 2024\Photoshop.exe",
}

# ─── QUICK-ACCESS FOLDERS ─────────────────────────────────────────────────────
FOLDERS = {
    "downloads"   : os.path.expanduser(r"~\Downloads"),
    "documents"   : os.path.expanduser(r"~\Documents"),
    "desktop"     : os.path.expanduser(r"~\Desktop"),
    "pictures"    : os.path.expanduser(r"~\Pictures"),
    "project"     : r"c:\Users\PATHAN\ai ml",   # ← your AI/ML project folder
    "storage"     : STORAGE_DIR,
}

# ─── VOICE SETTINGS ───────────────────────────────────────────────────────────
VOICE_RATE   = 175   # Words per minute (slower = clearer)
VOICE_VOLUME = 0.95  # 0.0 – 1.0

# ─── ML SETTINGS ──────────────────────────────────────────────────────────────
CONFIDENCE_THRESHOLD = 0.45   # Below this → ask user to repeat
