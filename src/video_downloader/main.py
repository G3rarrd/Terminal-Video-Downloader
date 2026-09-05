


from src.video_downloader.frontend.app import TerminalVideoDownloadManagerApp
from src.video_downloader.service.download_event_bus import DownloadEventBus

from .service.download_service import DownloadService
from .service.download_manager import DownloadManager


event_bus = DownloadEventBus()

download_manager = DownloadManager(event_bus, 3)

service = DownloadService(download_manager)

app = TerminalVideoDownloadManagerApp(service)
app.run()

download_manager.shutdown()
# def main():
    

# if __name__ == "__main__":
#     main()