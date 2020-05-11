from transcriptor.job import Job
from transcriptor.markers import Marker
import pytest

test_job_no_speakers = Job(
        name='Test Job',
        base_text= 'Ipsum maiores ducimus'
        speakers=[],
        markers=[
            Marker(end_time=1.0),
            Marker(
                start_time=1.1,
                end_time=2.0,
                ),
            Marker(
                start_time=2.1,
                end_time=3.0,
                ),
            ]
        transcription = None
        transcription_items = ([{'start_time'=
            start_time=1.1,
            end_time=2.0,
            alternatives=['Ipsum']}])

        )

def test_text_at_marker():
    markers = 
