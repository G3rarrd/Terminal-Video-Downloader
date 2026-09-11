from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from yt_dlp.utils import DownloadCancelled

from src.video_downloader.backend.yt_dlp.downloader import YtDlpDownloader
from src.video_downloader.models.download_job import CancellationToken, DownloadJob
from src.video_downloader.models.download_progress import JobStatus
from src.video_downloader.models.format_info import FormatInfo, FormatType

@pytest.fixture
def downloader():
    return YtDlpDownloader()


def make_format(format_id="137", format_type=FormatType.VIDEO_ONLY, **overrides):
    defaults = dict(
        format_id=format_id, extension="mp4", resolution=None, width=None, height=None,
        fps=None, filesize=None, filesize_approx=None, video_codec="avc1", audio_codec="none",
        audio_ext=None, video_ext=None, bitrate=None, video_bitrate=None, audio_bitrate=None,
        format_note=None, protocol="https", format_type=format_type,
    )
    defaults.update(overrides)
    return FormatInfo(**defaults)


def make_job(video_format=None, audio_format=None, **overrides):
    defaults = dict(
        id="job1",
        url="https://youtube.com/watch?v=abc",
        output_dir=Path("/tmp"),
        filename=None,
        ext=None,
        video_format=video_format,
        audio_format=audio_format,
        title="Test Video",
        domain="youtube.com",
        duration=120,
        thumbnail=None,
    )
    defaults.update(overrides)
    return DownloadJob(**defaults)

def test_build_selector_both_video_and_audio_selected(downloader):
    video = make_format(format_id="137", format_type=FormatType.VIDEO_ONLY)
    audio = make_format(format_id="140", format_type=FormatType.AUDIO_ONLY)

    result = downloader._build_selector(video, audio)

    assert result == "137+140/137"
    
def test_build_selector_video_only_picks_best_audio(downloader):
    video = make_format(format_id="137", format_type=FormatType.VIDEO_ONLY)

    result = downloader._build_selector(video, None)

    assert result == "137+bestaudio/137"
    
def test_build_selector_combined_video_format_no_audio_appended(downloader):
    # video_fmt exists but is COMBINED, not VIDEO_ONLY -- should NOT get "+bestaudio"
    combined = make_format(format_id="18", format_type=FormatType.COMBINED)

    result = downloader._build_selector(combined, None)

    assert result == "18"

def test_build_selector_audio_only_selected(downloader):
    audio = make_format(format_id="140", format_type=FormatType.AUDIO_ONLY)

    result = downloader._build_selector(None, audio)

    assert result == "140"

def test_build_selector_unknown_only_selected(downloader):
    # Assuming that all unknown formats are most likely videos if shown
    unknown = make_format(format_id="217", format_type=FormatType.AUDIO_ONLY)

    result = downloader._build_selector(unknown, None)

    assert result == "217"
    
def test_build_selector_neither_selected_raises_or_returns_none(downloader):
    # fmt = video_fmt or audio_fmt -- if both are None, fmt is None,
    # and fmt.format_id will raise AttributeError. This documents that
    # the caller must never invoke this with both None.
    with pytest.raises(ValueError, match="At least one of video_fmt or audio_fmt"):
        downloader._build_selector(None, None)
        
def test_build_progress_downloading_computes_percent(downloader):
    job = make_job()
    data = {"status": "downloading", "downloaded_bytes": 50, "total_bytes": 200, "speed": 1000, "eta": 5}

    result = downloader._build_progress(job, data)

    assert result.status == JobStatus.DOWNLOADING
    assert result.progress_pct == 25.0
    assert result.downloaded_bytes == 50
    assert result.total_bytes == 200
    # confirm the side-effect state was updated too
    assert downloader._downloaded_bytes == 50
    assert downloader._total_bytes == 200
    
def test_build_progress_downloading_falls_back_to_estimate(downloader):
    job = make_job()
    data = {"status": "downloading", "downloaded_bytes": 10, "total_bytes_estimate": 100}

    result = downloader._build_progress(job, data)

    assert result.total_bytes == 100
    assert result.progress_pct == 10.0

def test_build_progress_downloading_no_total_avoids_division_by_zero(downloader):
    job = make_job()
    data = {"status": "downloading", "downloaded_bytes": 10}  # no total at all

    result = downloader._build_progress(job, data)

    assert result.progress_pct == 0.0
    assert result.total_bytes == 0


def test_build_progress_finished(downloader):
    job = make_job()
    result = downloader._build_progress(job, {"status": "finished"})

    assert result.status == JobStatus.PROCESSING
    assert result.progress_pct == 100.0
    
def test_build_progress_error(downloader):
    job = make_job()
    result = downloader._build_progress(job, {"status": "error", "error": "network timeout"})

    assert result.status == JobStatus.ERROR
    assert result.error == "network timeout"
    
def test_build_progress_unknown_status_returns_none(downloader):
    job = make_job()
    assert downloader._build_progress(job, {"status": "some_future_status"}) is None

def test_build_progress_missing_status_key_returns_none(downloader):
    job = make_job()
    assert downloader._build_progress(job, {}) is None
    
def test_on_ytdlp_progress_raises_when_cancelled(downloader):
    job = make_job()
    token = MagicMock(spec=CancellationToken)
    token.is_cancelled.return_value = True
    publish = MagicMock()
    
    with pytest.raises(DownloadCancelled):
        downloader._on_ytdlp_progress(job, {"status": "downloading"}, publish, token)
        
    publish.assert_not_called()
    
def test_on_ytdlp_progress_publishes_when_not_cancelled(downloader):
    job = make_job()
    token = MagicMock(spec=CancellationToken)
    token.is_cancelled.return_value = False
    publish = MagicMock()
    data = {"status": "downloading", "downloaded_bytes": 5, "total_bytes": 10}
    
    downloader._on_ytdlp_progress(job, data, publish, token)
    
    publish.assert_called_once()
    published_arg = publish.call_args[0][0]
    assert published_arg.status == JobStatus.DOWNLOADING
    
def test_on_ytdlp_progress_skips_publish_on_unknown_status(downloader):
    job = make_job()
    token = MagicMock(spec=CancellationToken)
    token.is_cancelled.return_value = False
    publish = MagicMock()

    downloader._on_ytdlp_progress(job, {"status": "weird"}, publish, token)

    publish.assert_not_called()
    
def test_download_publishes_starting_then_completed(downloader):
    job = make_job(video_format=make_format(format_id="137", format_type=FormatType.VIDEO_ONLY))
    publish = MagicMock()
    token = MagicMock(spec=CancellationToken)
    token.is_cancelled.return_value = False
    
    mock_ydl_instance = MagicMock()
    
    with patch("src.video_downloader.backend.yt_dlp.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl_instance
        
        downloader.download(job, publish, token)
    
    statuses = [c.args[0].status for c in publish.call_args_list]
    assert statuses == [JobStatus.STARTING, JobStatus.COMPLETED]
    mock_ydl_instance.download.assert_called_once_with([job.url])

def test_download_builds_correct_format_selector(downloader):
    video = make_format(format_id="137", format_type=FormatType.VIDEO_ONLY)
    job = make_job(video_format=video)
    publish = MagicMock()
    token = MagicMock(spec=CancellationToken)

    with patch("src.video_downloader.backend.yt_dlp.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls, \
         patch("src.video_downloader.backend.yt_dlp.downloader.get_ytdlp_opts") as mock_get_opts:
        mock_ydl_cls.return_value.__enter__.return_value = MagicMock()
        mock_get_opts.return_value = {}

        downloader.download(job, publish, token)

        passed_extra_opts = mock_get_opts.call_args[0][0]
        assert passed_extra_opts["format"] == "137+bestaudio/137"

def test_download_publishes_error_and_reraises_on_generic_exception(downloader):
    job = make_job(video_format=make_format())
    publish = MagicMock()
    token = MagicMock(spec=CancellationToken)

    with patch("src.video_downloader.backend.yt_dlp.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.download.side_effect = RuntimeError("network exploded")
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl_instance

        with pytest.raises(RuntimeError):
            downloader.download(job, publish, token)

    statuses = [c.args[0].status for c in publish.call_args_list]
    assert statuses == [JobStatus.STARTING, JobStatus.ERROR]
    error_progress = publish.call_args_list[1].args[0]
    assert error_progress.error == "network exploded"

def test_download_publishes_cancelled_and_reraises(downloader):
    job = make_job(video_format=make_format())
    publish = MagicMock()
    token = MagicMock(spec=CancellationToken)

    with patch("src.video_downloader.backend.yt_dlp.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls:
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.download.side_effect = DownloadCancelled("cancelled by user")
        mock_ydl_cls.return_value.__enter__.return_value = mock_ydl_instance

        with pytest.raises(DownloadCancelled):
            downloader.download(job, publish, token)

    statuses = [c.args[0].status for c in publish.call_args_list]
    assert statuses == [JobStatus.STARTING, JobStatus.CANCELLED]
    

def test_download_output_template_uses_job_filename_or_title_fallback(downloader):
    job = make_job(video_format=make_format(), filename="custom_name")
    publish = MagicMock()
    token = MagicMock(spec=CancellationToken)

    with patch("src.video_downloader.backend.yt_dlp.downloader.yt_dlp.YoutubeDL") as mock_ydl_cls, \
         patch("src.video_downloader.backend.yt_dlp.downloader.get_ytdlp_opts") as mock_get_opts:
        mock_ydl_cls.return_value.__enter__.return_value = MagicMock()
        mock_get_opts.return_value = {}

        downloader.download(job, publish, token)

        outtmpl = mock_get_opts.call_args[0][0]["outtmpl"]
        assert "custom_name.%(ext)s" in outtmpl