import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import FOLDERS, STORAGE_DIR

def execute_web(intent: str, entity: str | None, raw_text: str = "") -> dict:
    response = ""
    action = None
    url = None

    if intent == "OPEN_BROWSER":
        response = "I'd open your browser, but this is a web app! You're already in one."
        action = "message"

    elif intent in ("OPEN_NOTEPAD", "OPEN_CALCULATOR", "OPEN_VSCODE", "RUN_COMMAND"):
        response = f"'{intent}' is a desktop-only action. This web version can't open local apps."
        action = "message"

    elif intent == "OPEN_FOLDER":
        response = "Opening folders is a desktop feature. In the web version, I can save and find files for you instead."
        action = "message"

    elif intent == "WEB_SEARCH":
        query = entity or raw_text
        if query:
            url = f"https://www.google.com/search?q={query}"
            response = f"Searching Google for \"{query}\"."
            action = "open_url"
        else:
            response = "What would you like me to search for?"
            action = "message"

    elif intent == "PLAY_MEDIA":
        query = entity or raw_text
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            response = f"Searching YouTube for \"{query}\"."
            action = "open_url"
        else:
            response = "What should I search on YouTube?"
            action = "message"

    elif intent == "SAVE_TEXT":
        response = "__SAVE_FLOW__"
        action = "save_flow"

    elif intent == "FIND_FILE":
        from memory.storage_manager import StorageManager
        sm = StorageManager()
        if entity:
            result = sm.find_file(entity)
            if result:
                response = f"Found it! Saved at: {result}"
                action = "message"
            else:
                response = f"Sorry, I couldn't find any file matching '{entity}'."
                action = "message"
        else:
            response = "What file are you looking for?"
            action = "message"

    elif intent == "CREATE_FOLDER":
        name = entity or "new_folder"
        name = "".join(c for c in name if c.isalnum() or c in (" ", "_", "-")).strip()
        name = name.replace(" ", "_") or "new_folder"
        path = os.path.join(STORAGE_DIR, name)
        os.makedirs(path, exist_ok=True)
        response = f"Created folder '{name}' in Nexus storage."
        action = "message"

    elif intent == "GOODBYE":
        response = "Goodbye! Nexus is shutting down. Have a great day!"
        action = "goodbye"

    elif intent == "UNKNOWN":
        if raw_text:
            url = f"https://www.google.com/search?q={raw_text}"
            response = f"I wasn't sure about that, so I searched Google for it."
            action = "open_url"
        else:
            response = "I'm not sure what you mean. Could you rephrase that?"
            action = "message"

    else:
        if raw_text:
            url = f"https://www.google.com/search?q={raw_text}"
            response = f"I recognized this as {intent}, but I don't have a web action for it. Searching Google."
            action = "open_url"
        else:
            response = f"I recognized your intent as {intent}, but I don't have a web action for that yet."
            action = "message"

    result = {"response": response, "action": action}
    if url:
        result["url"] = url
    return result
