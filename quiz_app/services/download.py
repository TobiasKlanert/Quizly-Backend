"""Helpers to download YouTube audio to a temp file for quiz generation."""

import os
import tempfile
import yt_dlp


def download_audio_to_temp(url: str, preferred_codec: str = 'm4a'):
    """
    This function uses yt_dlp to fetch the best available audio stream from a given
    YouTube URL (or any URL supported by yt_dlp) and runs FFmpegExtractAudio to
    convert/extract the audio into a standalone file.
    Args:
        url (str): YouTube video URL or any yt_dlp-compatible media identifier.
        preferred_codec (str, optional): Desired audio codec/extension to produce
            (for example 'm4a', 'mp3'). Default is 'm4a'. yt_dlp/FFmpeg will be
            instructed to produce this codec, but the actual produced extension may
            differ depending on available formats and FFmpeg behavior.
    Returns:
        str: Absolute path to the temporary audio file created (including extension).
             The file is created with a unique base name in the system temporary
             directory and will have an audio file extension appended by yt_dlp/FFmpeg.
    Raises:
        FileNotFoundError: If yt_dlp does not produce any audio file for the given URL.
        OSError: If temporary file creation/removal or other filesystem operations fail.
    Side effects and behavior notes:
        - A unique temporary base filename is created and removed so that yt_dlp
          can create the final file with the expected extension.
        - The function configures yt_dlp to download 'bestaudio/best', be quiet,
          and to avoid playlist downloads. It uses the FFmpegExtractAudio
          postprocessor to request conversion to `preferred_codec`.
        - If the file with the preferred extension is not found after download,
          the function probes a list of common audio extensions ('m4a', 'mp3',
          'wav', 'aac', 'ogg', 'flac') and returns the first match.
        - The caller is responsible for deleting the returned temporary file when
          it is no longer needed to avoid accumulating temporary files.
    Example:
        path = download_audio_to_temp('https://www.youtube.com/watch?v=...')
        # use the audio file ...
        os.remove(path)  # caller must clean up the temp file
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
