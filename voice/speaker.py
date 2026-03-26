"""
voice/speaker.py — Text-to-Speech using pyttsx3 (offline)
"""

import pyttsx3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import VOICE_RATE, VOICE_VOLUME

_engine = None


def _get_engine() -> pyttsx3.Engine:
    """Lazily initialize and reuse the TTS engine (singleton)."""
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate",   VOICE_RATE)
        _engine.setProperty("volume", VOICE_VOLUME)

        # Prefer a female voice if available
        voices = _engine.getProperty("voices")
        for v in voices:
            if "zira" in v.name.lower() or "female" in v.name.lower():
                _engine.setProperty("voice", v.id)
                break

    return _engine


def speak(text: str) -> None:
    """
    Speaks the given text aloud using the system TTS engine.

    Args:
        text: The string to speak.
    """
    print(f"🤖  Nexus: {text}")
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    speak("Hello! I am Nexus, your hands-free operating system. How can I help you today?")
