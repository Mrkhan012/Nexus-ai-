"""
executor/actions.py — Maps Nexus intents to real OS actions.
"""

import os
import sys
import subprocess
import webbrowser

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import APPS, FOLDERS


def _open_app(app_key: str) -> str:
    """Open an application by its config key. Returns a feedback message."""
    path = APPS.get(app_key)
    if path and os.path.exists(path):
        subprocess.Popen([path])
        return f"Sure, I'm opening {app_key} for you."
    else:
        # Fallback: try via Windows start command
        subprocess.Popen(f'start {app_key}', shell=True)
        return f"Okay, I'm trying to open {app_key}."


def _open_folder(entity: str | None) -> str:
    """Open a known folder by entity keyword, or file explorer as fallback."""
    if entity:
        for key, path in FOLDERS.items():
            if key in entity or entity in key:
                subprocess.Popen(f'explorer "{path}"', shell=True)
                return f"Opening your {key} folder now."
    # Default: open file explorer
    subprocess.Popen("explorer", shell=True)
    return "Sure, opening file explorer."


# ─── Intent → Action Map ──────────────────────────────────────────────────────

def execute(intent: str, entity: str | None, raw_text: str = "") -> str:
    """
    Execute the action corresponding to the given intent.

    Args:
        intent   : Classified intent string (e.g. "OPEN_BROWSER").
        entity   : Extracted entity/name from the user's speech.
        raw_text : Original user speech (for advanced extraction if needed).

    Returns:
        A response string to speak back to the user.
    """

    if intent == "OPEN_BROWSER":
        # Try Chrome first, then Edge, then system default
        chrome = APPS.get("chrome", "")
        edge   = APPS.get("edge",   "")
        if os.path.exists(chrome):
            subprocess.Popen([chrome])
            return "Google Chrome is opening."
        elif os.path.exists(edge):
            subprocess.Popen([edge])
            return "Microsoft Edge is opening."
        else:
            webbrowser.open("https://www.google.com")
            return "I'll open your default browser for you."

    elif intent == "OPEN_NOTEPAD":
        return _open_app("notepad")

    elif intent == "OPEN_CALCULATOR":
        return _open_app("calculator")

    elif intent == "OPEN_VSCODE":
        path = APPS.get("vscode", "")
        if os.path.exists(path):
            subprocess.Popen([path])
            return "Opening VS Code. Just a moment."
        else:
            subprocess.Popen("code", shell=True)
            return "VS Code is starting up."

    elif intent == "OPEN_FOLDER":
        return _open_folder(entity)

    elif intent == "WEB_SEARCH":
        query = entity or raw_text
        if query:
            url = f"https://www.google.com/search?q={query}"
            import webbrowser
            webbrowser.open(url)
            return f"Certainly! Searching Google for {query}."
        return "I'm ready. What would you like me to search for?"

    elif intent == "PLAY_MEDIA":
        query = entity or raw_text
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            import webbrowser
            webbrowser.open(url)
            return f"Playing {query} on YouTube."
        return "Of course. What should I play on YouTube?"

    elif intent == "SAVE_TEXT":
        # Handled by main.py which provides the content
        return "__SAVE_FLOW__"   # Signal main loop to enter save flow

    elif intent == "FIND_FILE":
        # Import here so circular imports are avoided
        from memory.storage_manager import StorageManager
        sm = StorageManager()
        if entity:
            result = sm.find_file(entity)
            if result:
                folder = os.path.dirname(result)
                subprocess.Popen(f'explorer "{folder}"', shell=True)
                return f"Found it! Opening the folder containing {entity}. Path: {result}"
            else:
                return f"Sorry, I couldn't find any file matching '{entity}' in my memory."
        return "What file are you looking for? Please say a name."

    elif intent == "CREATE_FOLDER":
        name = entity or "new_folder"
        # Sanitize name
        name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        name = name.replace(" ", "_")
        from config import STORAGE_DIR
        path = os.path.join(STORAGE_DIR, name)
        os.makedirs(path, exist_ok=True)
        subprocess.Popen(f'explorer "{path}"', shell=True)
        return f"Done! I've created the folder '{name}' in your Nexus storage."

    elif intent == "RUN_COMMAND":
        if entity:
            try:
                result = subprocess.run(
                    entity, shell=True,
                    capture_output=True, text=True, timeout=15
                )
                output = result.stdout.strip() or result.stderr.strip()
                return f"Command executed. Output: {output[:200]}" if output else "Command executed."
            except subprocess.TimeoutExpired:
                return "Command timed out."
            except Exception as e:
                return f"Could not run command: {e}"
        return "What command should I run?"

    elif intent == "GOODBYE":
        return "__EXIT__"   # Signal main loop to exit

    elif intent == "UNKNOWN":
        # Enhanced Fallback: If unknown, offer to search the web
        if raw_text:
            url = f"https://www.google.com/search?q={raw_text}"
            import webbrowser
            webbrowser.open(url)
            return f"I wasn't sure about '{raw_text}', so I'm searching Google for it."
        return "I'm not sure what you mean. Could you rephrase that?"

    else:
        # Default fallback for any other string the user says
        if raw_text:
            url = f"https://www.google.com/search?q={raw_text}"
            import webbrowser
            webbrowser.open(url)
            return f"I recognized this as {intent}, but since I don't have a specific action, I'm searching Google for you."
        return f"I recognized your intent as {intent}, but I don't have an action for that yet."
