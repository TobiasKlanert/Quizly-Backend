import re
from django.core.validators import RegexValidator


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
