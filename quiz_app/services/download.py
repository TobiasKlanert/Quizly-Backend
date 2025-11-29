import os
import tempfile
import yt_dlp


def download_audio_to_temp(url: str, preferred_codec: str = 'm4a'):
    """Download the audio track of a YouTube video into a temporary file.

    Returns the path to the temporary audio file (including extension).
    Caller is responsible for deleting the file when no longer needed.
    """
    # Create a unique temporary filename (we remove the file because yt_dlp
    # will create files based on the `outtmpl` and add the audio extension).
    fd, base_path = tempfile.mkstemp(prefix='quizly_audio_')
    os.close(fd)
    try:
        os.unlink(base_path)
    except OSError:
        pass

    outtmpl = base_path
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'quiet': True,
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': preferred_codec,
        }]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    final_path = f"{base_path}.{preferred_codec}"
    if not os.path.exists(final_path):
        # Try common audio extensions if the preferred one wasn't created
        for ext in ('m4a', 'mp3', 'wav', 'aac', 'ogg', 'flac'):
            p = f"{base_path}.{ext}"
            if os.path.exists(p):
                final_path = p
                break

    if not os.path.exists(final_path):
        raise FileNotFoundError('Audio file was not created by yt_dlp')

    return final_path
