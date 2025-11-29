import os
import re

from typing import Optional
from urllib.parse import urlparse, parse_qs

from .download import download_audio_to_temp
from .transcription import transcribe_audio
from core.common.clients.gemini import generate_quiz


def _strip_code_fences(text: str) -> str:
    """Remove wrapping triple-backtick code fences (e.g. ```json ... ```)."""
    if not text:
        return text
    s = text.strip()
    # remove leading fence like ``` or ```json
    s = re.sub(r'^\s*```[^\n]*\n?', '', s, count=1)
    # remove trailing fence
    s = re.sub(r'\n?```\s*$', '', s, count=1)
    return s.strip()


def build_quiz_from_youtube(
    url: str,
    whisper_model: str = "turbo",
    gemini_model: str = "gemini-2.5-flash",
) -> str:
    """
    Download audio from a YouTube URL, transcribe it and generate a quiz with Gemini.
    Returns the quiz (string, expected to be JSON).
    The temporary audio file is deleted before returning.
    Raises exceptions from the underlying steps on failure.
    """

    temp_path: Optional[str] = None
    try:
        temp_path = download_audio_to_temp(url)
        transcript = transcribe_audio(temp_path, whisper_model)
        quiz = generate_quiz(transcript, model=gemini_model)
        return _strip_code_fences(quiz)
    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass
