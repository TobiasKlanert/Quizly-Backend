import os
import re
import json

from typing import Optional

from .download import download_audio_to_temp
from .transcription import transcribe_audio
from core.common.clients.gemini import generate_quiz


class InvalidQuizError(Exception):
    """Raised when the generated quiz is not valid JSON or does not match the expected shape."""
    pass


def _strip_code_fences(text: str) -> str:
    """Remove wrapping triple-backtick code fences (e.g. ```json ... ```)."""
    if not text:
        return text
    s = text.strip()
    s = re.sub(r'^\s*```[^\n]*\n?', '', s, count=1)
    s = re.sub(r'\n?```\s*$', '', s, count=1)
    return s.strip()


def build_quiz_from_youtube(
    url: str,
    whisper_model: str = "turbo",
    gemini_model: str = "gemini-2.5-flash",
) -> dict:
    """
    Download audio from a YouTube URL, transcribe it and generate a quiz with Gemini.
    Returns a dict (parsed JSON) matching the expected quiz structure.
    Raises InvalidQuizError if the returned text cannot be parsed to JSON.
    """
    temp_path: Optional[str] = None
    try:
        temp_path = download_audio_to_temp(url)
        transcript = transcribe_audio(temp_path, whisper_model)
        quiz_text = generate_quiz(transcript, model=gemini_model)

        # strip code fences -> still a string
        stripped = _strip_code_fences(quiz_text)
        if not stripped:
            raise InvalidQuizError("Blank answer from the quiz generator.")

        # If generate_quiz already returned a dict, handle that too:
        if isinstance(stripped, dict):
            return stripped

        # now parse JSON
        try:
            quiz_obj = json.loads(stripped)
        except json.JSONDecodeError as e:
            # optionally: include underlying text in logs but not in error to client
            raise InvalidQuizError(
                "The response provided by the generator is not valid JSON.") from e
        return quiz_obj

    finally:
        if temp_path:
            try:
                os.remove(temp_path)
            except Exception:
                pass
