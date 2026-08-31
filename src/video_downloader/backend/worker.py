import queue
import asyncio
from threading import Thread


from video_downloader.backend.models.download_job import DownloadJob

def worker(name : str, job_queue: queue.Queue) :
    while True:
        job = job_queue.get()
        try:
            if not job:
                break
            
            download_video(job)
        except Exception as exc:
            print(f"{name} failed: {exc}")
        finally:
            job_queue.task_done()

def process():
    input_queue = queue.Queue()

    for i in range(3):
        Thread(
            target=worker,
            args=(f"Worker_{i}", input_queue),
            daemon=True,
        ).start()
        

if __name__ == "__main__":
    process()