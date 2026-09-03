# src/video_downloader/backend/config.py
from typing import Any, Dict, Optional
from yt_dlp.networking.impersonate import ImpersonateTarget

def get_ytdlp_opts(
    extra_opts: Optional[Dict[str, Any]] = None,
    cookie_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Base options for yt-dlp with anti-bot evasion and curl-cffi TLS impersonation."""
    opts: Dict[str, Any] = {
        "impersonate": "firefox",
        "quiet": True,
        "no_warnings": True,
    }
    
    opts["impersonate"] = ImpersonateTarget.from_str(opts["impersonate"].lower())
    
    if cookie_path:
        opts["cookiefile"] = cookie_path

    if extra_opts:
        opts.update(extra_opts)

    return opts