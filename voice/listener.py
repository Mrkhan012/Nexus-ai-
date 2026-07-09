"""
voice/listener.py — Speech-to-Text via sounddevice (Python 3.14 compatible).

Uses sounddevice to capture microphone audio, converts it to a WAV buffer,
then passes it to SpeechRecognition + Google STT for transcription.
Falls back to keyboard input if sounddevice is also unavailable.
"""

import sys
import os
import io
import wave
import struct
import subprocess
import contextlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─── Check sounddevice availability ───────────────────────────────────────────
_SD_AVAILABLE = False
try:
    import sounddevice as sd
    import numpy as np
    _SD_AVAILABLE = True
except (ImportError, OSError):
    pass

SAMPLE_RATE  = 16000   # 16kHz — optimal for Google STT
CHANNELS     = 1
DTYPE        = "int16"


def _record_audio(duration: int = 6) -> bytes | None:
    """
    Record audio from the microphone for `duration` seconds.
    Returns raw PCM bytes (int16), or None on error.
    """
    try:
        print(f"\n🎙️  Nexus is listening... (speak now, up to {duration}s)")
        recording = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocking=True,
        )
        sd.wait()
        return recording.tobytes()
    except Exception as e:
        print(f"🎤  Microphone error: {e}")
        return None


def _pcm_to_wav_bytes(pcm_data: bytes) -> bytes:
    """Wrap raw PCM bytes into a WAV byte stream for SpeechRecognition."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)        # int16 = 2 bytes
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    buf.seek(0)
    return buf


@contextlib.contextmanager
def _safe_subprocess_stderr():
    """
    Work around Windows `OSError: [WinError 50] The request is not supported`.

    SpeechRecognition's `recognize_google` shells out to the bundled `flac`
    encoder. When `stderr` is left to inherit, Python tries to DuplicateHandle
    the parent's stderr — which fails in some Windows consoles/IDEs where that
    handle isn't a real, duplicatable handle. Forcing `stderr=DEVNULL` gives the
    child a fresh, inheritable handle instead, sidestepping the failure.
    """
    _orig_popen = subprocess.Popen

    class _PatchedPopen(_orig_popen):
        def __init__(self, *args, **kwargs):
            if kwargs.get("stderr") is None:
                kwargs["stderr"] = subprocess.DEVNULL
            super().__init__(*args, **kwargs)

    subprocess.Popen = _PatchedPopen
    try:
        yield
    finally:
        subprocess.Popen = _orig_popen


def _listen_sounddevice(phrase_limit: int = 6) -> str | None:
    """Record mic → WAV → Google STT → text string."""
    import speech_recognition as sr

    pcm = _record_audio(duration=phrase_limit)
    if pcm is None:
        return None

    wav_buf = _pcm_to_wav_bytes(pcm)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_buf) as source:
        audio = recognizer.record(source)

    try:
        with _safe_subprocess_stderr():
            text = recognizer.recognize_google(audio)
        print(f"🗣️  You said: \"{text}\"")
        return text.lower().strip()
    except sr.UnknownValueError:
        print("❓  Could not understand. Please speak clearly.")
        return None
    except sr.RequestError as e:
        print(f"🌐  Google STT error: {e}")
        return None


# ─── Keyboard fallback ────────────────────────────────────────────────────────
def _listen_keyboard() -> str | None:
    print("\n⌨️  [KEYBOARD MODE] sounddevice not available.")
    try:
        text = input("   Type your command: ").strip().lower()
        return text if text else None
    except (EOFError, KeyboardInterrupt):
        return None


# ─── Public API ───────────────────────────────────────────────────────────────
def listen(timeout: int = 8, phrase_limit: int = 6) -> str | None:
    """
    Captures user input — voice via sounddevice, or keyboard as fallback.
    `phrase_limit` controls max recording seconds in voice mode.
    """
    if _SD_AVAILABLE:
        return _listen_sounddevice(phrase_limit=phrase_limit)
    else:
        return _listen_keyboard()


def is_voice_mode() -> bool:
    """Returns True if microphone (sounddevice) input is active."""
    return _SD_AVAILABLE


if __name__ == "__main__":
    mode = "🎙️ Voice (sounddevice)" if is_voice_mode() else "⌨️ Keyboard"
    print(f"Input mode: {mode}")
    result = listen()
    print("Heard:", result)

