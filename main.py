"""
main.py — Nexus: Hands-Free OS Voice Assistant
Entry point. Runs the continuous listen → classify → execute loop.

Usage:
    python main.py

First-time setup:
    pip install -r requirements.txt
    python brain/trainer.py
    python main.py
"""

import os
import sys
import time

# ─── Module Imports ───────────────────────────────────────────────────────────
from voice.listener        import listen
from voice.speaker         import speak
from brain.classifier      import classify
from executor.actions      import execute
from memory.storage_manager import StorageManager
from config                import MODEL_PATH, CONFIDENCE_THRESHOLD

BANNER = r"""
  _   _                    
 | \ | | _____  ___   _ ___ 
 |  \| |/ _ \ \/ / | | / __|
 | |\  |  __/>  <| |_| \__ \
 |_| \_|\___/_/\_\\__,_|___/

   Your Hands-Free Operating System
"""


def ensure_model_trained():
    """Auto-train the model on first run if model file doesn't exist."""
    if not os.path.exists(MODEL_PATH):
        speak("First-time setup. Training my brain. This will only take a moment.")
        print("🏗️  Model not found. Training now...")
        from brain.trainer import train
        train()
        speak("Training complete. I am ready.")


def save_flow(sm: StorageManager) -> str:
    """
    Interactive save flow: ask user for file name and content.
    Returns a response message.
    """
    speak("What would you like to name this file?")
    name_text = listen(timeout=6)
    if not name_text:
        return "No file name detected. Save cancelled."

    speak(f"Got it. And what is the content you want to save?")
    content_text = listen(timeout=10, phrase_limit=30)
    if not content_text:
        return "No content detected. Save cancelled."

    path = sm.save_text(name_text, content_text, tags=name_text)
    return f"Saved! Your file '{name_text}' is stored at: {path}"


def main():
    print(BANNER)
    print("=" * 50)

    # Ensure model is ready
    ensure_model_trained()

    # Initialize storage
    sm = StorageManager()

    speak("Welcome! Nexus is online and ready for your commands.")
    print("\n✅  Nexus is running. Speak a command (or say 'bye Nexus' to stop).\n")
    print("─" * 50)

    retry_count = 0
    MAX_RETRIES = 3

    while True:
        # ── Listen ──────────────────────────────────────────────────────────
        speak("I'm listening.")
        raw_text = listen()

        if raw_text is None:
            retry_count += 1
            if retry_count >= MAX_RETRIES:
                speak("I'm having trouble hearing you. Please check your microphone.")
                retry_count = 0
            else:
                speak("I didn't catch that. Please try again.")
            continue

        retry_count = 0  # Reset on successful listen

        # ── Classify ────────────────────────────────────────────────────────
        intent, confidence, entity = classify(raw_text)
        print(f"   🧠  Intent={intent}  Confidence={confidence:.2f}  Entity={entity}")

        # ── Execute ─────────────────────────────────────────────────────────
        response = execute(intent, entity, raw_text)

        # ── Special Signals from executor ───────────────────────────────────
        if response == "__EXIT__":
            speak("Goodbye! Nexus shutting down. Have a great day!")
            print("\n👋  Nexus shut down. Goodbye!")
            break

        elif response == "__SAVE_FLOW__":
            response = save_flow(sm)

        # ── Speak Response ───────────────────────────────────────────────────
        speak(response)
        print("─" * 50)
        time.sleep(0.3)   # Brief pause before re-listening


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔  Interrupted by user.")
        speak("Nexus interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌  Unexpected error: {e}")
        import traceback
        traceback.print_exc()
