import yt_dlp
from pathlib import Path
from pprint import pprint
from src.video_downloader.config.paths import DOWNLOAD_DIR
from video_downloader.backend.yt_dlp.extractor import YtDlpExtractor
from video_downloader.backend.yt_dlp.format_processor import FormatProcessor
from video_downloader.backend.yt_dlp.format_presenter import FormatPresenter
from video_downloader.backend.models.download_job import DownloadJob
from video_downloader.backend.yt_dlp.downloader import YtDlpDownloader


while True:
    
    url = input("Enter video URL: ")
    extractor = YtDlpExtractor()

    meta_data = extractor.extract_metadata(url)
    format_list = meta_data.formats

    if not format_list:
        continue
    
    processor = FormatProcessor()
    presenter = FormatPresenter()
    print("Video Formats")
    
    video_formats = processor.get_video_formats(format_list)
    for i, fmt in enumerate(video_formats):
        print(i, presenter.video_row(fmt))
        
    format_id = int(input("Select Format ID: "))
    print(video_formats[format_id], "was chosen")
    job = DownloadJob(url=url, format=video_formats[format_id], filename="video_test")
    
    downloader = YtDlpDownloader()
    downloader.download(job)
        
    
    
    # print("Audio Formats")
    # audio_formats = processor.get_audio_formats(format_list)
    # for i, fmt in enumerate(audio_formats):
    #     print(i, presenter.audio_row(fmt))
    # pprint(meta_data)
    
