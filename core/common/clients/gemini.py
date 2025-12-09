"""Client utilities for generating quizzes via Google Gemini."""

import os
from pathlib import Path

from dotenv import load_dotenv, dotenv_values
from google import genai

# Prefer loading from the project .env.
BASE_DIR = Path(__file__).resolve().parents[3]
load_dotenv(BASE_DIR / ".env")


# The client gets the API key from the environment variable `GEMINI_API_KEY`.

def get_client():
    """Create and return a configured genai.Client.

    Reads the GEMINI_API_KEY from the .env file located at BASE_DIR / ".env" using dotenv_values.
    If the environment variable is missing or empty, raises a RuntimeError with a clear message
    instructing the user to add GEMINI_API_KEY to the .env file.

    Returns:
      genai.Client: A genai client instance initialized with the retrieved API key.

    Raises:
      RuntimeError: If GEMINI_API_KEY is not set in the .env file.
    """
    api_key = dotenv_values(BASE_DIR / ".env").get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to your .env file before calling generate_quiz()."
        )
    return genai.Client(api_key=api_key)


TEMPLATE = '''Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{

  "title": "Create a concise quiz title based on the topic of the transcript.",

  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",

  "questions": [

    {{

      "question_title": "The question goes here.",

      "question_options": ["Option A", "Option B", "Option C", "Option D"],

      "answer": "The correct answer from the above options"

    }},

    ...

    (exactly 10 questions)

  ]

}}

Requirements:

- Each question must have exactly 4 distinct answer options.

- Only one correct answer is allowed per question, and it must be present in 'question_options'.

- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).

- Do not include explanations, comments, or any text outside the JSON.

- Transcript: 

'''


def generate_quiz(transcript, model="gemini-2.5-flash"):
    """
    Generate a quiz from a transcript using a Gemini model.

    Parameters
    ----------
    transcript : str
      The transcript text to use as source material. This text is appended to the module-level
      TEMPLATE to form the prompt sent to the Gemini API.
    model : str, optional
      The identifier of the Gemini model to use (default: "gemini-2.5-flash").

    Returns
    -------
    str
      The textual quiz content produced by the Gemini API (taken from response.text).

    Raises
    ------
    RuntimeError
      If required credentials (e.g., GEMINI_API_KEY) are missing and get_client() cannot
      construct a working client.

    Notes
    -----
    - This function performs network I/O by calling get_client() and then client.models.generate_content.
    - Prompt construction relies on a module-level TEMPLATE variable.
    - Errors from the underlying client (network errors, API errors) may propagate to the caller.
    """
    client = get_client()
    prompt = TEMPLATE + transcript
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
