from pathlib import Path

DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

SYSTEM_DOWNLOAD_PATH = Path.home()