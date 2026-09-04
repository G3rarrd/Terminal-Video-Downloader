


from src.video_downloader.frontend.app import TerminalVideoDownloadManagerApp

from .service.download_service import DownloadService
from .service.download_manager import DownloadManager



download_manager = DownloadManager(3)

service = DownloadService(download_manager)

app = TerminalVideoDownloadManagerApp(service)
app.run()

download_manager.shutdown()
# def main():
    

# if __name__ == "__main__":
#     main()