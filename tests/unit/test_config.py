import pytest
from yt_dlp.networking.impersonate import ImpersonateTarget
from src.video_downloader.backend.yt_dlp.config import get_ytdlp_opts

def test_default_opts_have_expected_keys():
    opts = get_ytdlp_opts()
    
    assert opts["quiet"] is True
    assert opts["no_warnings"] is True
    assert opts["js_runtimes"] == {"deno": {}, "node": {}}

def test_default_opts_no_cookiefile():
    opts = get_ytdlp_opts()
    assert "cookiefile" not in opts
    
def test_impersonate_is_converted_to_target_object():
    opts = get_ytdlp_opts()
    
    assert isinstance(opts["impersonate"], ImpersonateTarget)
    # the base default should be firefox
    assert opts["impersonate"] == ImpersonateTarget.from_str("firefox")
    
def test_cookie_path_sets_cookiefile():
    opts = get_ytdlp_opts(cookie_path="/tmp/cookies.txt")
    assert opts["cookiefile"] == "/tmp/cookies.txt"

def test_cookie_path_none_omits_cookiefile():
    opts = get_ytdlp_opts(cookie_path=None)
    assert "cookiefile" not in opts

def test_extra_opts_adds_new_keys():
    opts = get_ytdlp_opts(extra_opts={"format" : "bestvideo+bestaudio"})
    assert opts["format"] == "bestvideo+bestaudio"
    # ensures the original opts are not replaced
    assert opts["quiet"] is True
    
def test_extra_opts_overrides_existing_key():
    opts = get_ytdlp_opts(extra_opts={"quiet": False})
    assert opts["quiet"] is False
    
def test_extra_opts_empty_dict_is_noop():
    opts_with_empty = get_ytdlp_opts(extra_opts={})
    opts_without = get_ytdlp_opts()
    assert opts_with_empty == opts_without