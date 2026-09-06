from textual.message import Message

from src.video_downloader.models.download_job import DownloadJob


class JobAdded(Message):
    """Posted when the add download button is clicked."""

    def __init__(self, job : DownloadJob) -> None:
        super().__init__()
        self.job = job