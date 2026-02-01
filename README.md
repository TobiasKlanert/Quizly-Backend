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
- A `.env` file in the project root with `GEMINI_API_KEY=<your-key>`, `SECRET_KEY=<your-django-secret>`, and any host/origin overrides.
- (Optional) GPU for faster Whisper transcription; first run downloads the Whisper model.

## Getting Started (Local)
### 1) Clone and enter the project directory

```
git clone https://github.com/TobiasKlanert/Quizly-Backend.git
cd Quizly-Backend
```

### 2) Create and activate a virtual environment

```
python -m venv env
# Windows
.\env\Scripts\activate
# macOS/Linux
source env/bin/activate
```

### 3) Install dependencies

```
pip install -r requirements.txt
```

### 4) Set environment variables in .env

Create a `.env` file in the project root (or edit the existing one) and add:

```
GEMINI_API_KEY=your-key
SECRET_KEY=your-django-secret
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500
```

Commands to create it quickly:
```
# macOS/Linux (creates or overwrites)
cat <<'EOF' > .env
GEMINI_API_KEY=your-key
SECRET_KEY=your-django-secret
ALLOWED_HOSTS=127.0.0.1,localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500
EOF

# Windows PowerShell (creates or overwrites)
Set-Content .env "GEMINI_API_KEY=your-key"
Add-Content .env "SECRET_KEY=your-django-secret"
Add-Content .env "ALLOWED_HOSTS=127.0.0.1,localhost"
Add-Content .env "CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500"
```

### 5) Apply migrations 

```
python manage.py migrate
```

### 6) (Optional) Create an admin user to access `/admin/`

```
python manage.py createsuperuser
```

### 7) Run the development server

```
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.


# Docker Setup Guide

This guide walks you through cloning the repository, configuring environment variables, building the Docker containers, and starting the server.

## 1) Clone the repository

```
git clone https://github.com/TobiasKlanert/Quizly-Backend.git
cd Quizly-Backend
```

## 2) Create the environment file

Copy the example and edit it:

```
copy .env.example .env
```

Open `.env` and set at least:
- `DJANGO_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `GEMINI_API_KEY`

## 3) Create the external Docker network (required for Caddy)

```
docker network create web
```

## 4) Build and start the containers

```
docker compose up -d --build
```

## 5) Run database migrations

```
docker compose exec app python manage.py migrate
```

## 6) (Optional) Create an admin user

```
docker compose exec app python manage.py createsuperuser
```

## 7) Start or restart the server

If the containers are already running, you can restart them with:

```
docker compose restart
```

The API will be available on the internal container port `8000` and should be exposed via your reverse proxy (Caddy).


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
3. Google Gemini (core/common/clients/gemini.py, model `gemini-2.5-flash`) builds quiz JSON; `GEMINI_API_KEY` must be set in `.env`.
4. Serializers validate that each question has exactly four options and a matching answer before storing.

## Configuration Notes
- `SECRET_KEY`: Currently hardcoded for development. For production, set this from an environment variable and keep it secret.
- `DEBUG`: Set to `True` for development. Must be `False` in production.
- `ALLOWED_HOSTS`: Add your domain(s) or IPs for production.
- `DATABASES`: Uses SQLite by default. Switch to Postgres/MySQL for production.
- `CORS_ALLOWED_ORIGINS`: Add your frontend origin(s). Defaults to `http://127.0.0.1:5500`.
- Cookies are set with secure=True and samesite=Lax; browsers require HTTPS to persist them. For local HTTP testing, consider toggling secure in auth_app/api/views.py.

## Troubleshooting
- Missing cookies in the browser? Ensure you are using HTTPS or relax the secure flag for local development.
- yt_dlp errors like FFmpegExtractAudio -> install FFmpeg and confirm it is on PATH.
- RuntimeError: GEMINI_API_KEY is not set -> add it to `.env` before starting the server.
- Long first request times come from Whisper downloading models; this is expected.
