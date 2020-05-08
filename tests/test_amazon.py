import pytest
from transcriptor import amazon


def test_add_speaker_creates_speaker_object():
    """Amazon add_speaker creates a speaker object"""
    speaker = amazon.add_speaker(0)
    assert speaker.base_name == 'spk_0'
    assert speaker.speaker_index == 0


def test_add_marker_creates_marker_object_with_speaker():
    """Amazon add_marker creates a marker object"""
    segment = {
            "start_time": "0.44",
            "speaker_label": "spk_0",
            "end_time": "3.3",
            }

    marker = amazon.add_marker(segment, has_speakers=True)
    assert marker.speaker == amazon.add_speaker(0)
    assert marker.start_time == 0.44
    assert marker.end_time == 3.3
