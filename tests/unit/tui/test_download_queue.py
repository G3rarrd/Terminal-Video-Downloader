import pytest
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.video_downloader.frontend.widgets.download_queue.download_item import DownloadItem
from src.video_downloader.frontend.widgets.download_queue.download_queue import DownloadQueue
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService

@pytest.fixture
def mock_service():
    return MagicMock(spec=DownloadService)


@pytest.fixture
def queue(mock_service):
    return DownloadQueue(service=mock_service)
    
def make_job(job_id="job1", output_dir=None, filename="video", ext="mp4", **overrides):
    defaults = dict(
        id=job_id,
        url="https://youtube.com/watch?v=abc",
        output_dir=output_dir or Path("/tmp"),
        filename=filename,
        ext=ext,
        video_format=None,
        audio_format=None,
        title="Test", domain="youtube.com", duration=120, thumbnail=None,
    )
    defaults.update(overrides)
    return DownloadJob(**defaults)

def test_cancel_job_does_nothing_when_no_selection(queue, mock_service):
    queue.selected_item = None

    queue.cancel_job()

    mock_service.cancel_job.assert_not_called()
    
def test_cancel_job_does_nothing_when_selected_item_has_no_job(queue, mock_service):
    fake_item = MagicMock(spec=DownloadItem)
    fake_item.job = None
    
    queue.selected_item = fake_item

    queue.cancel_job()

    mock_service.cancel_job.assert_not_called()
    
def test_cancel_job_calls_service_with_job_id(queue, mock_service):
    job = make_job(job_id="job42")
    fake_item = MagicMock(spec=DownloadItem)
    fake_item.job = job
    queue.selected_item = fake_item

    queue.cancel_job()

    mock_service.cancel_job.assert_called_once_with("job42")
    
def test_open_job_notifies_warning_when_item_has_not_been_highlighted(queue, mock_service):
    queue.selected_item = None
    queue.notify = MagicMock()
    
    
    queue.open_job()
    
    queue.notify.assert_called_once()