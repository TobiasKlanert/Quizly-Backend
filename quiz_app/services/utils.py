import re
from django.core.validators import RegexValidator


"""
Utility definitions for validating YouTube URLs used by the quiz application.
This module provides:
- YOUTUBE_REGEX: a compiled regular expression that matches common YouTube URL forms
    and captures the 11-character video identifier in a named group "id".
- YOUTUBE_URL_VALIDATOR: a Django RegexValidator instance configured with YOUTUBE_REGEX,
    a user-facing error message, and an error code for integration with Django forms/models.
Behavior and supported URL formats:
- Matches full and partial URLs with optional scheme:
        https://www.youtube.com/watch?v=VIDEOID
        http://youtube.com/watch?v=VIDEOID
        www.youtube.com/watch?v=VIDEOID
        youtube.com/watch?v=VIDEOID
- Matches shortened YouTube URLs:
        https://youtu.be/VIDEOID
        youtu.be/VIDEOID
- Matches YouTube Shorts URLs:
        https://www.youtube.com/shorts/VIDEOID
- The VIDEOID is expected to be exactly 11 characters long, consisting of word characters
    (letters, digits, underscore) and hyphens.
- Query parameters or fragments following the ID are allowed and ignored by the capture.
- Matching is case-insensitive.
Usage examples:
- Extract the video id:
        match = YOUTUBE_REGEX.match(url)
        if match:
                video_id = match.group("id")
- Use in Django model or form field:
        url = models.URLField(validators=[YOUTUBE_URL_VALIDATOR])
Limitations:
- The regex validates common URL shapes but does not verify that the video actually exists
    on YouTube or that the ID corresponds to an accessible resource.
- Nonstandard but valid YouTube URL variants (e.g., additional path segments before the ID)
    may not be matched.
Error reporting:
- YOUTUBE_URL_VALIDATOR uses message "Invalid YouTube-URL." and code "invalid_youtube_url".
"""

YOUTUBE_REGEX = re.compile(
    r'^(https?://)?(www\.)?'
    r'(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)'
    r'(?P<id>[\w-]{11})'
    r'([&?].*)?$',
    re.IGNORECASE
)

YOUTUBE_URL_VALIDATOR = RegexValidator(
    regex=YOUTUBE_REGEX,
    message="Invalid YouTube-URL.",
    code="invalid_youtube_url",
)
