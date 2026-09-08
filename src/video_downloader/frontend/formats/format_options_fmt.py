from collections import defaultdict

from src.video_downloader.models.format_info import FormatInfo
def get_ljust(video_formats: list[FormatInfo]) -> dict[str, int]:
    """ Get the maximum length of the individual video formats options string columns"""
    res = defaultdict(int)
    if not video_formats:
        return res

    for vf in video_formats:
        # Use the exact same fallback values used in _format_label
        res_str = vf.resolution or "?"
        codec_str = vf.video_codec or "?"
        size_str = _fmt_filesize(vf.filesize)
        ext_str = vf.extension or "?"

        res["resolution"] = max(res["resolution"], len(res_str))
        res["vcodec"] = max(res["vcodec"], len(codec_str))
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
    codec = (fmt.video_codec or "?").ljust(ljust_map["vcodec"])
    size = _fmt_filesize(fmt.filesize).rjust(ljust_map["size"])
    extension = (fmt.extension or "?").ljust(ljust_map["ext"])

    return f"{resolution} · {codec} · {size} · {extension}"