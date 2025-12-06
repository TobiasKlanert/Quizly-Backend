"""Client utilities for generating quizzes via Google Gemini."""

import os
from google import genai


# The client gets the API key from the environment variable `GEMINI_API_KEY`.

def get_client():
    """Create and return a genai.Client. Raise a clear error if API key is missing."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Set it in the environment before calling generate_quiz()."
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
    """Generate a quiz from transcript. Raises RuntimeError if GEMINI_API_KEY missing."""
    client = get_client()
    prompt = TEMPLATE + transcript
    response = client.models.generate_content(model=model, contents=prompt)
    return response.text
