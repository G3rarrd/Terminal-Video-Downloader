import pytest

from src.video_downloader.backend.yt_dlp.format_processor import FormatProcessor
from src.video_downloader.models.format_info import FormatType
from tests.conftest import make_format

@pytest.fixture
def processor():
    return FormatProcessor()

def test_remove_invalid_drops_none_format_id(processor):
    valid = make_format(format_id="1")
    invalid = make_format(format_id=None)
    
    result = processor._remove_invalid([valid, invalid])
    assert result == [valid]
    
def test_remove_invalid_empty_list(processor):
    assert processor._remove_invalid([]) == []
    
    
def test_select_best_video_formats_picks_higher_bitrate(processor):
    low = make_format(format_id="low", height=1080, extension="mp4", video_codec="avc1", video_bitrate=500)
    high = make_format(format_id="high", height=1080, extension="mp4", video_codec="avc1", video_bitrate=1500)
    
    result = processor._select_best_video_formats([low, high])
    
    assert result == [high]
    
def test_select_best_video_formats_keeps_distinct_resolutions(processor):
    p720 = make_format(format_id="720p", height=720, extension="mp4", video_codec="avc1")
    p1080 = make_format(format_id="1080p", height=1080, extension="mp4", video_codec="avc1")

    result = processor._select_best_video_formats([p720, p1080])

    assert {f.format_id for f in result} == {"720p", "1080p"}
    
def test_select_best_video_formats_none_bitrate_treated_as_zero(processor):
    none_bitrate = make_format(format_id="a", height=1080, extension="mp4",
                                video_codec="avc1", video_bitrate=None)
    zero_bitrate = make_format(format_id="b", height=1080, extension="mp4",
                                video_codec="avc1", video_bitrate=0)

    result = processor._select_best_video_formats([none_bitrate, zero_bitrate])
    # first-seen wins since neither beats the other (0 > 0 is False)
    assert result == [none_bitrate]
    
    
def test_select_best_audio_formats_picks_higher_bitrate(processor):
    low = make_format(format_id="low", audio_codec="opus", extension="webm", audio_bitrate=64)
    high = make_format(format_id="high", audio_codec="opus", extension="webm", audio_bitrate=160)

    result = processor._select_best_audio_formats([low, high])

    assert result == [high]
        
def test_select_best_audio_formats_distinct_codec_extension_both_kept(processor):
    opus = make_format(format_id="opus", audio_codec="opus", extension="webm")
    aac = make_format(format_id="aac", audio_codec="mp4a.40.2", extension="m4a")

    result = processor._select_best_audio_formats([opus, aac])

    assert len(result) == 2
    
def test_get_video_formats_filters_out_audio_only(processor):
    video = make_format(format_id="v", height=1080, video_codec="avc1",
                         format_type=FormatType.VIDEO_ONLY)
    
    audio = make_format(format_id="a", audio_codec="opus",
                         format_type=FormatType.AUDIO_ONLY)

    combined = make_format(format_id="a", audio_codec="opus",
                         format_type=FormatType.COMBINED)
    result = processor.get_video_formats([video, combined, audio])

    assert result == [video, combined]
    
    
def test_get_video_formats_fallback_when_all_unknown(processor):
    # The fallback: if filtering leaves nothing, return the pre-filter list
    unknown1 = make_format(format_id="u1", height=720, format_type=FormatType.UNKNOWN)
    unknown2 = make_format(format_id="u2", height=1080, format_type=FormatType.UNKNOWN)

    result = processor.get_video_formats([unknown1, unknown2])

    assert len(result) == 2
    assert {f.format_id for f in result} == {"u1", "u2"}

def test_get_video_formats_excludes_invalid_before_fallback(processor):
    # invalid formats should never reappear via the fallback
    invalid = make_format(format_id=None, format_type=FormatType.UNKNOWN)
    unknown = make_format(format_id="u", height=720, format_type=FormatType.UNKNOWN)

    result = processor.get_video_formats([invalid, unknown])

    assert result == [unknown]

def test_get_audio_formats_only_returns_audio_only_type(processor):
    audio = make_format(format_id="a", audio_codec="opus",
                         format_type=FormatType.AUDIO_ONLY)
    video = make_format(format_id="v", video_codec="avc1",
                         format_type=FormatType.VIDEO_ONLY)
    combined = make_format(format_id="c", format_type=FormatType.COMBINED)

    result = processor.get_audio_formats([audio, video, combined])

    assert result == [audio]

def test_get_audio_formats_has_no_fallback(processor):
    # unlike get_video_formats, this has no fallback -- confirms that's intentional
    video_only = make_format(format_id="v", format_type=FormatType.VIDEO_ONLY)

    result = processor.get_audio_formats([video_only])

    assert result == []