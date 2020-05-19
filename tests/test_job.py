from transcriptor.job import Job
from transcriptor.alternatives import Alternative
from transcriptor.markers import Marker
from transcriptor.speakers import Speaker
import pytest

speaker_1 = Speaker(base_name='spk_0', name='Jay')
speaker_2 = Speaker(base_name='spk_1', name=None)

test_job = Job(
        name='Test Job',
        base_text= 'Ipsum maiores ducimus',
        speakers=[speaker_1, speaker_2],
        markers=[
            Marker(
                speaker=speaker_1,
                start_time=0.0,
                end_time=1.0,
                ),
            Marker(
                speaker=speaker_2,
                start_time=1.1,
                end_time=3.0,
                ),
            ],
        transcription = None,
        alternatives = [
            Alternative(
                content='Ipsum',
                start_time=0.1,
                end_time=1.0,
                confidence=1.0,
                _type="pronunciation"
            ),
            Alternative(
                content='maiores',
                start_time=1.1,
                end_time=2.0,
                confidence=1.0,
                _type="pronunciation"
            ),
            Alternative(
                content='ducimus',
                start_time=2.1,
                end_time=3.0,
                confidence=1.0,
                _type="pronunciation"
            ),
            Alternative(
                content='.',
                confidence=0.0,
                _type="punctuation"
            ),
        ]
    )


def test_text_at_marker():
    """Return all text between the start/stop time of markers"""

    t = test_job
    assert t.get_text_at_marker(t.markers[0]) == 'Ipsum'
    assert t.get_text_at_marker(t.markers[1]) == 'maiores ducimus.'


def test_job_as_text():
    assert test_job.as_text() == 'Jay 0.0:\n\nIpsum\n\nspk_1 1.1:\n\nmaiores ducimus.'


def test_job_no_speakers():
    assert test_job.as_text(has_speaker=False) == '0.0:\n\nIpsum\n\n1.1:\n\nmaiores ducimus.'


def test_job_as_text_picks_up_changes_to_speaker():
    test_job.speakers[1].name = 'Alice'
    assert test_job.speakers[1].name == 'Alice'
    assert test_job.as_text() == 'Jay 0.0:\n\nIpsum\n\nAlice 1.1:\n\nmaiores ducimus.'
