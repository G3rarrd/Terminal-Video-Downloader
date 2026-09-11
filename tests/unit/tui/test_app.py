import pytest
from unittest.mock import MagicMock

from src.video_downloader.frontend.app import TerminalVideoDownloadManagerApp
from src.video_downloader.frontend.modals.download_modal import DownloadModal
from src.video_downloader.frontend.widgets.download_queue.download_queue import DownloadQueue
from src.video_downloader.models.download_job import DownloadJob
from src.video_downloader.service.download_service import DownloadService


@pytest.fixture
def mock_service():
    return MagicMock(spec=DownloadService)

@pytest.fixture
def app(mock_service) -> TerminalVideoDownloadManagerApp:
    return TerminalVideoDownloadManagerApp(service=mock_service)

async def test_app_mounts_download_manager_screen(app):
    async with app.run_test() as pilot:
        assert app.screen.id == "download-screen"
        
        
async def test_pressing_a_opens_add_download_modal(app):
    async with app.run_test() as pilot:
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(app.screen, DownloadModal)
        
def test_on_modal_closed_with_job_adds_to_queue(app):
    fake_job = MagicMock(spec=DownloadJob)
    app._get_download_queue = MagicMock()
    mock_queue = app._get_download_queue.return_value
    
    app._on_modal_closed(fake_job)
    mock_queue.add_job.assert_called_once_with(fake_job)

def test_on_modal_closed_with_none_does_nothing(app):
    app._get_download_queue = MagicMock()

    app._on_modal_closed(None)

    app._get_download_queue.assert_not_called()
    

def test_action_cancel_download_delegates_to_queue(app):
    app._get_download_queue = MagicMock()
    
    app.action_cancel_download()
    
    mock_queue = app._get_download_queue.return_value
    
    mock_queue.cancel_job.assert_called_once()


def test_action_open_download_delegates_to_queue(app):
    app._get_download_queue = MagicMock()

    app.action_open_download()

    mock_queue = app._get_download_queue.return_value
    
    mock_queue.open_job.assert_called_once()
    
async def test_get_download_queue_finds_widget_on_screen(app):
    async with app.run_test() as pilot:

        queue = app._get_download_queue()
        assert isinstance(queue, DownloadQueue)  