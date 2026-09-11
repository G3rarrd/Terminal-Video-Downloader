import os
from pathlib import Path
import platform
import re
import subprocess
import unicodedata


def clean_filename(text: str) -> str:
    # Normalize Unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove characters invalid on Windows/macOS/Linux
    text = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Windows doesn't like filenames ending with these
    text = text.rstrip(". ")

    # Avoid empty filenames
    if not text:
        text = "download"

    return text



def start_file(self, filepath : Path):
    system = platform.system()

    if system == "Windows":
        os.startfile(filepath)

    elif system == "Darwin":
        subprocess.run(["open", str(filepath)], check=False)

    elif system == "Linux":
        subprocess.run(["xdg-open", str(filepath)], check=False)

