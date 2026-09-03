import re
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