def transcribe_audio(file_path: str, whisper_model: str = 'turbo') -> str:
    """
    Transcribe an audio file to text using the whisper package.
    This function attempts to import the whisper module at runtime and, if
    available, loads the requested whisper model to transcribe the audio file
    located at file_path. The transcription text (if present) is returned as a
    string.
    - Parameters
        - file_path : str
            Path to the audio file to be transcribed. The path should point to a
            file format supported by the installed whisper backend.
        - whisper_model : str, optional
            Name of the whisper model to load (default: 'turbo'). The exact model
            names available depend on the installed whisper implementation.
    - Returns
        - str
            The transcribed text. If the underlying transcription result does not
            contain a 'text' field, an empty string is returned.
    - Raises
        - RuntimeError
            If the whisper package is not installed or no transcription backend is
            available.
        - Exception
            Any exceptions raised by the whisper package when loading the model or
            during transcription are propagated to the caller.
    - Notes
        - The function imports whisper lazily; installing or upgrading the whisper
            package after the program starts will not be detected unless the process
            re-imports the module or restarts.
        - The semantics and available model names depend on the whisper package
            implementation/version installed in the environment.
    """
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
