from transcriptor.job import Job
from transcriptor.markers import Marker
from transcriptor.speakers import Speaker
from transcriptor.alternatives import Alternative

import boto3
import more_itertools
import requests
import typing

transcribe = boto3.client('transcribe')

def add_speaker(speaker_index: int) -> Speaker:
    """Create a speaker object from one of the labels in results['speaker_labels']"""
    return Speaker(
            base_name=f'spk_{speaker_index}',
            )


def add_marker(
        segment: typing.Sequence,
        *,
        has_speakers:bool=False,
        start_time=0.0,
        end_time=0.0,
        ) -> typing.Dict:
    """Create a Marker object using the speaker time_stamps OR the defined
    item_segments if speakers is False"""

    if has_speakers:
        speaker = segment['speaker_label']
        start_time = float(segment.get('start_time', start_time))
        end_time = float(segment.get('end_time', end_time))

    else:
        speaker = None
        start_time = float(segment[0]['start_time'])

        if len(segment) >= 2:
            end_time = float(segment[-2]['end_time'])

        else:
            end_time = float(segment[-1]['end_time'])

    return {
            'speaker': speaker,
            'start_time': start_time,
            'end_time': end_time,
           }


def add_alternative(segment:typing.Dict, start_time=0.0, end_time=0.0) -> Alternative:
        return Alternative(
                content = segment['alternatives'][0]['content'],
                _type = segment['type'],
                confidence = float(segment['alternatives'][0]['confidence']),
                start_time = float(segment.get('start_time', start_time)),
                end_time = float(segment.get('end_time', end_time)),
                )


def from_job(job_name: str) -> Job:
    """Create a Job Object based on the TranscriptiobJobName"""
    job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
    return from_uri(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])


def from_uri(uri) -> Job:
    """Create a Job Object based on the TranscriptFileUri"""
    response = requests.get(uri)
    response.raise_for_status()

    return from_json(response.json())

def from_json(transcription) -> Job:
    """Create a Job Object when given an Amazon JSON Object"""
    if 'speaker_labels' in transcription['results']:
        labels = transcription['results']['speaker_labels']
        speakers = [add_speaker(x) for x in range(labels['speakers'])]
        markers = [add_marker(x, has_speakers=True) for x in labels['segments']]

    else:
        segments = transcription['results']['items']
        speakers = []
        items_segments = more_itertools.split_when(
            segments, lambda x,y: x['alternatives'][0]['content'] in ['.', '?', '!'],
        )
        markers = []
        start_time = 0.0
        end_time = 0.0

        for marker_object in items_segments:
            marker = add_marker(
                    marker_object,
                    start_time=start_time,
                    end_time=end_time,
            )
            markers.append(marker)
            start_time = marker['start_time']
            end_time = marker['end_time']

    alternatives = []
    start_time = 0.0
    end_time = 0.0

    for alternative_object in transcription['results']['items']:
        alternative = add_alternative(
            alternative_object,
            start_time=start_time,
            end_time=end_time,
            )
        alternatives.append(alternative)
        start_time = alternative.start_time
        end_time = alternative.end_time

    return Job.from_amazon(
            base_text = transcription['results']['transcripts'][0]['transcript'],
            alternatives = alternatives,
            name = transcription['jobName'],
            transcription=transcription,
            speakers = speakers,
            markers = markers,
            )
