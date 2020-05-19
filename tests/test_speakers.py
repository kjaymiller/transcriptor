import pytest
from transcriptor.speakers import Speaker


def test_speaker_label_returns_name_if_present():
    """If there is a 'name' value then use it as the label"""
    test_speaker = Speaker(base_name='spk_0', name='Jay')
    assert test_speaker.label == 'Jay'


def test_speaker_label_returns_base_name_if_name_missing():
    """If there is no 'name' value then use the base_name as the label"""
    test_speaker = Speaker(base_name='spk_0')
    assert test_speaker.label == 'spk_0'
