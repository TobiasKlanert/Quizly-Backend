# Quizly Backend

Backend service that turns YouTube videos into multiple-choice quizzes using Django, Whisper transcription, and Google Gemini. JWT auth uses http-only cookies; quizzes are stored per user.

## Features
- User registration/login with JWT via http-only cookies plus refresh/logout.
- Quiz builder pipeline: yt-dlp downloads audio (FFmpeg required), Whisper transcribes, Gemini generates a structured quiz, then data is saved.
- Quiz CRUD: create from a YouTube URL, list user quizzes, retrieve/update/delete individual quizzes.
- CORS preconfigured for local frontend at http://127.0.0.1:5500; Django admin available.

## Prerequisites
- Python 3.11+ and pip/virtualenv.
- FFmpeg installed and available on PATH (required by yt-dlp and Whisper).
- Network access to YouTube and Google Gemini APIs.
- Environment variable `GEMINI_API_KEY` set to a valid key.
- (Optional) GPU for faster Whisper transcription; first run downloads the Whisper model.

## Quickstart
1. Create and activate a virtual environment:
   - Windows: py -m venv env && .\\env\\Scripts\\activate
   - macOS/Linux: python3 -m venv env && source env/bin/activate
2. Install dependencies: pip install -r requirements.txt
3. Set the Gemini key:
   - Windows: set GEMINI_API_KEY=your-key
   - macOS/Linux: export GEMINI_API_KEY=your-key
4. Apply migrations: python manage.py migrate
5. (Optional) Create an admin user: python manage.py createsuperuser
6. Start the dev server: python manage.py runserver
7. Open http://127.0.0.1:8000/admin/ for Django admin or hit the API endpoints under /api/.

## API Reference
Authentication (cookies are `access_token` + `refresh_token`):
- POST /api/register/ with { "username": "...", "email": "...", "password": "...", "confirmed_password": "..." }
- POST /api/login/ with { "username": "...", "password": "..." } -> returns basic user info and sets cookies.
- POST /api/logout/ -> clears cookies (requires authentication).
- POST /api/token/refresh/ -> refreshes the access token using the refresh cookie.

Quizzes (all require authentication):
- POST /api/createQuiz/ with { "url": "https://youtu.be/<video>" } -> downloads audio, transcribes, generates a 10-question quiz, saves, and returns it.
- GET /api/quizzes/ -> list quizzes for the logged-in user.
- GET /api/quizzes/<id>/ -> retrieve a single quiz.
- PATCH /api/quizzes/<id>/ -> partial update.
- DELETE /api/quizzes/<id>/ -> delete.

## Quiz Generation Pipeline
1. yt_dlp downloads the YouTube audio track (needs FFmpeg).
2. openai-whisper transcribes the audio (quiz_app/services/transcription.py, model `turbo` by default).
3. Google Gemini (core/common/clients/gemini.py, model `gemini-2.5-flash`) builds quiz JSON; `GEMINI_API_KEY` must be set.
4. Serializers validate that each question has exactly four options and a matching answer before storing.

## Configuration Notes
- Default DB is SQLite at db.sqlite3; update DATABASES in core/settings.py for other backends.
- CORS_ALLOWED_ORIGINS is set to http://127.0.0.1:5500. Adjust for your frontend host(s).
- Cookies are set with secure=True and samesite=Lax; browsers require HTTPS to persist them. For local HTTP testing, consider toggling secure in auth_app/api/views.py.
- DEBUG=True by default; set DEBUG=False and configure ALLOWED_HOSTS for production.

## Troubleshooting
- Missing cookies in the browser? Ensure you are using HTTPS or relax the secure flag for local development.
- yt_dlp errors like FFmpegExtractAudio -> install FFmpeg and confirm it is on PATH.
- RuntimeError: GEMINI_API_KEY is not set -> export the key before starting the server.
- Long first request times come from Whisper downloading models; this is expected.
