
from src.video_downloader.frontend.app import TerminalVideoDownloadManagerApp

from .backend.download_service import DownloadService
from .backend.download_manager import DownloadManager
from .backend.yt_dlp.downloader import YtDlpDownloader


download_manager = DownloadManager(3)

service = DownloadService(download_manager)

app = TerminalVideoDownloadManagerApp(service)

app.run()

download_manager.shutdown()
# def main():
    

# if __name__ == "__main__":
#     main()