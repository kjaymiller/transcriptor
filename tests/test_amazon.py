import pytest
import requests
import requests_mock
from transcriptor import amazon

segment = {
        "speaker_label": "spk_0",
        "start_time": "0.44",
        "end_time": "3.3",
        }

no_speaker_segment = {
        "speaker_label": "spk_0",
        "start_time": "0.44",
        "end_time": "3.3",
        }

test_job_no_speaker = {
        'jobName': 'TestJob',
        'results': {
                'transcripts': [
                    {'transcript': 'Lorem consequatur nesciunt...'},
                    ],
                'items': [no_speaker_segment]
                }
        }


def test_add_speaker_creates_speaker_object():
    """Amazon add_speaker creates a speaker object"""
    speaker = amazon.add_speaker(0)
    assert speaker.base_name == 'spk_0'
    assert speaker.speaker_index == 0


def test_add_marker_creates_marker_object_with_speaker():
    """Amazon add_marker creates a marker object"""
    marker = amazon.add_marker(segment, has_speakers=True)
    assert marker.speaker == amazon.add_speaker(0)
    assert marker.start_time == 0.44
    assert marker.end_time == 3.3

def test_from_amazon_uri_gets_job_json_from_uri(requests_mock, mocker):
    '''Given a uri, fetch JSON'''

    requests_mock.get(
            'https://example.com/example_job.json',
            json=test_job_no_speaker,
            )
    mocker.patch('transcriptor.amazon.Job')
    job = amazon.from_amazon_uri('https://example.com/example_job.json')
    amazon.Job.assert_called()
