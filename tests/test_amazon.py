import pytest
from transcriptor.amazon import add_speaker

def test_add_speaker_creates_speaker_object():
    t_speaker = add_speaker(0)
    assert t_speaker.base_name == 'spk_0'
    assert t_speaker.speaker_index == 0

