

def transcribe_audio(file_path: str, whisper_model: str = 'turbo') -> str:
    try:
        import whisper
    except Exception:
        whisper = None

    if whisper is not None:
        model = whisper.load_model(whisper_model)
        result = model.transcribe(file_path)
        return result.get('text', '')

    raise RuntimeError(
        'No transcription backend available: install `whisper`')
