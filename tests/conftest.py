import json
import pytest
from pathlib import Path

from src.video_downloader.models.format_info import FormatType

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "ytdlp_responses"

@pytest.fixture
def sample_formats():
    with open(FIXTURES_DIR / "sample_formats.json") as f:
        return json.load(f)
    
    
def test_classify_format_from_actual_response(extractor, sample_formats):
    cases = [
        ("storyboard", FormatType.UNKNOWN),
        ("dubbed_audio_null_acodec", FormatType.UNKNOWN),  # documents the yt-dlp quirk
        ("video_only_av1", FormatType.VIDEO_ONLY),
        ("combined_legacy_null_bitrates", FormatType.COMBINED),
        ("audio_only_opus", FormatType.AUDIO_ONLY),
    ]
    
    for key, expected in cases:
        fmt = sample_formats[key]
        result = extractor._classify_format(fmt["vcodec"], fmt["acodec"])
        assert result == expected, f"failed for case '{key}'"
        

# tests/conftest.py or a local helper in the test file
from src.video_downloader.models.format_info import FormatInfo, FormatType

def make_format(
    format_id="1",
    extension="mp4",
    height=None,
    video_codec="none",
    audio_codec="none",
    video_bitrate=None,
    audio_bitrate=None,
    format_type=FormatType.UNKNOWN,
    **overrides,
) -> FormatInfo:
    defaults = dict(
        format_id=format_id,
        extension=extension,
        resolution=None,
        width=None,
        height=height,
        fps=None,
        filesize=None,
        filesize_approx=None,
        video_codec=video_codec,
        audio_codec=audio_codec,
        audio_ext=None,
        video_ext=None,
        bitrate=None,
        video_bitrate=video_bitrate,
        audio_bitrate=audio_bitrate,
        format_note=None,
        protocol="https",
        format_type=format_type,
    )
    defaults.update(overrides)
    return FormatInfo(**defaults)