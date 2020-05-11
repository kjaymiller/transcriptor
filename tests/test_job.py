from transcriptor.job import Job
from transcriptor.alternatives import Alternative
from transcriptor.markers import Marker
import pytest

test_job_no_speakers = Job(
        name='Test Job',
        base_text= 'Ipsum maiores ducimus',
        speakers=[],
        markers=[
            Marker(
                start_time=0.0,
                end_time=1.0,
                ),
            Marker(
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
            ),
            Alternative(
                content='maiores',
                start_time=1.1,
                end_time=2.0,
                confidence=1.0,
            ),
            Alternative(
                content='ducimus',
                start_time=2.1,
                end_time=3.0,
                confidence=1.0,
            ),
            Alternative(
                content='.',
                start_time=3.1,
                end_time=4.0,
                confidence=1.0,
            ),

        ]
    )


def test_text_at_marker():
    """Return all text between the start/stop time of markers"""

    assert test_job_no_speakers.text_at_marker(0) == 'Ipsum'
    assert test_job_no_speakers.text_at_marker(1) == 'maiores ducimus'
