from collections import defaultdict

from src.video_downloader.models.format_info import FormatInfo, FormatType
def get_ljust(formats: list[FormatInfo]) -> dict[str, int]:
    """ Get the maximum length of the individual video formats options string columns"""
    res = defaultdict(int)
    if not formats:
        return res

    for f in formats:
        # Use the exact same fallback values used in _format_label
        res_str = f.resolution or "?"
        vcodec_str = _display_codec(f.video_codec)
        acodec_str = _display_codec(f.audio_codec)
        size_str = _fmt_filesize(f.filesize)
        ext_str = f.extension or "?"

        res["resolution"] = max(res["resolution"], len(res_str))
        res["acodec"] = max(res["acodec"], len(acodec_str))
        res["vcodec"] = max(res["vcodec"], len(vcodec_str))
        res["size"] = max(res["size"], len(size_str))
        res["ext"] = max(res["ext"], len(ext_str))

    return res

def _fmt_filesize(filesize: int | None) -> str:
    if not filesize:
        return "? MB"
    return f"{filesize / 1_000_000:.1f} MB"

def format_label(fmt: FormatInfo, ljust_map: dict[str, int]) -> str:
    """ Pad strings matching the pre-calculated maximum field widths """
    resolution = (fmt.resolution or "?").ljust(ljust_map["resolution"])
    vcodec = (_display_codec(fmt.video_codec)).ljust(ljust_map["vcodec"])
    acodec = (_display_codec(fmt.audio_codec)).ljust(ljust_map["acodec"])
    size = _fmt_filesize(fmt.filesize).ljust(ljust_map["size"])
    extension = (fmt.extension or "?").ljust(ljust_map["ext"])

    return f"{resolution} · {vcodec} · {acodec} · {size} · {extension}"

def _display_codec(codec: str | None) -> str:
    return "?" if codec in (None, "none") else codec