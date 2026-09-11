import pytest
from src.video_downloader.backend.yt_dlp.extractor import YtDlpExtractor
from src.video_downloader.models.format_info import FormatType
from unittest.mock import patch, MagicMock
from PIL import Image
import io

@pytest.fixture
def extractor() -> YtDlpExtractor:
    return YtDlpExtractor()

@pytest.mark.parametrize("vcodec,acodec,expected", [
    ("avc1.640028", "mp4a.40.2", FormatType.COMBINED),
    ("avc1.640028", "none", FormatType.VIDEO_ONLY),
    ("avc1.640028", None, FormatType.VIDEO_ONLY),
    ("none", "mp4a.40.2", FormatType.AUDIO_ONLY),
    (None, "mp4a.40.2", FormatType.AUDIO_ONLY),
    ("none", "none", FormatType.UNKNOWN),
    (None, None, FormatType.UNKNOWN),
])
def test_classify_format(extractor, vcodec, acodec, expected):
    assert extractor._classify_format(vcodec, acodec) == expected

@pytest.mark.parametrize("case_key,expected", [
    ("storyboard", FormatType.UNKNOWN),
    ("dubbed_audio_null_acodec", FormatType.UNKNOWN),
    ("video_only_av1", FormatType.VIDEO_ONLY),
    ("combined_legacy_null_bitrates", FormatType.COMBINED),
    ("audio_only_opus", FormatType.AUDIO_ONLY),
])
def test_classify_format_from_actual_response(extractor, sample_formats, case_key, expected):
    fmt = sample_formats[case_key]
    result = extractor._classify_format(fmt["vcodec"], fmt["acodec"])
    assert result == expected
    
    
def make_test_image_bytes():
    img = Image.new("RGB", (10, 10), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_fetch_thumbnail_success(extractor):
    fake_response = MagicMock()
    fake_response.content = make_test_image_bytes()
    fake_response.raise_for_status = MagicMock()
    
    with patch("src.video_downloader.backend.yt_dlp.extractor.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session.get.return_value = fake_response
        mock_session_cls.return_value.__enter__.return_value = mock_session
        
        img = extractor._fetch_thumbnail("https://example.com/thumb.png")
        
        assert img is not None
        assert img.size == (10, 10)
        mock_session.get.assert_called_once_with("https://example.com/thumb.png")
        
def test_fetch_thumbnail_none_url_returns_placeholder(extractor):
    with patch("src.video_downloader.backend.yt_dlp.extractor.create_broken_image_placeholder") as mock_placeholder:
        mock_placeholder.return_value = "PLACEHOLDER"
        result = extractor._fetch_thumbnail(None)
        assert result == "PLACEHOLDER"
        
def test_fetch_thumbnail_request_fails_returns_placeholder(extractor):
    with patch("src.video_downloader.backend.yt_dlp.extractor.requests.Session") as mock_session_cls, \
         patch("src.video_downloader.backend.yt_dlp.extractor.create_broken_image_placeholder") as mock_placeholder:

        mock_session = MagicMock()
        mock_session.get.side_effect = Exception("network error") 
        mock_session_cls.return_value.__enter__.return_value = mock_session
        mock_placeholder.return_value = "PLACEHOLDER"

        result = extractor._fetch_thumbnail("https://example.com/thumb.png")
        assert result == "PLACEHOLDER"