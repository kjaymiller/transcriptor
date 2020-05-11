import pytest
import requests
import requests_mock
from transcriptor import amazon


### SUPPORTING VARIABLES ###

speaker_segment = {
    "speakers": 4,
    "segments": [
        {
            "start_time": "0.44",
            "speaker_label": "spk_0",
            "end_time": "3.3",
            "items": [
                {"start_time": "0.44", "speaker_label": "spk_0", "end_time": "0.99",},
            ],
        }
    ],
}

no_speaker_segment = [
        {
            "alternatives": [{
                    "confidence" : 1.0,
                    "content" : "Lorem autem veritatis.",
                    }],
                    "start_time": "0.44",
                    "end_time": "3.3",
            }
        ]

test_job_no_speaker = {
    "jobName": "TestJob",
    "results": {
        "transcripts": [{"transcript": "Lorem consequatur nesciunt..."}],
        "items": no_speaker_segment,
    },
}


test_transcription_job_object = {
    "Transcript": {"TranscriptFileUri": "https://example.com/example_job.json"}
}
### TESTS ###


def test_add_speaker_creates_speaker_object():
    """Amazon add_speaker creates a speaker object"""
    speaker = amazon.add_speaker(0)
    assert speaker.base_name == "spk_0"
    assert speaker.speaker_index == 0


def test_add_marker_creates_marker_object_with_speaker():
    """Amazon add_marker creates a marker object"""
    marker = amazon.add_marker(speaker_segment["segments"][0], has_speakers=True)
    assert marker.speaker == amazon.add_speaker(0)
    assert marker.start_time == 0.44
    assert marker.end_time == 3.3


def test_add_alternative_creates_alternative_object():
    """Amazon add_alternative create an alternative object"""
    alternative = amazon.add_alternative(no_speaker_segment[0]) # no speaker segment is results['items']
    assert alternative.confidence == 1.0
    assert alternative.start_time == 0.44
    assert alternative.end_time == 3.3
    assert alternative.content == 'Lorem autem veritatis.'



def test_add_marker_creates_marker_object_with_no_speaker():
    """Amazon add_marker creates a marker object"""
    marker = amazon.add_marker(no_speaker_segment)
    assert marker.speaker == None
    assert marker.start_time == 0.44
    assert marker.end_time == 3.3


def test_amazon_from_uri_gets_job_json_from_uri(requests_mock, mocker):
    """Given a uri, fetch JSON"""

    requests_mock.get(
        "https://example.com/example_job.json", json=test_job_no_speaker,
    )
    mocker.patch("transcriptor.amazon.Job")
    job = amazon.from_uri("https://example.com/example_job.json")
    amazon.Job.assert_called()


def test_from_amazon_json(requests_mock, mocker):
    """Given a uri, fetch JSON"""

    requests_mock.get(
        "https://example.com/example_job.json", json=test_job_no_speaker,
    )

    mocker.patch(
        "transcriptor.amazon.transcribe.get_transcription_job",
        lambda TranscriptionJobName:test_transcription_job_object,
    )

    mocker.patch("transcriptor.amazon.Job")
    job = amazon.from_job('TestJobID')
    amazon.Job.assert_called()
