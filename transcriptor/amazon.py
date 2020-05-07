from job import Job
from markers import Marker

import boto3
import more_itertools
import requests
import typing

transcribe = boto3.client('transcribe')

def add_speaker(speaker_index):
    return Speaker(
            speaker_index: speaker_index,
            base_name: f'spk_{speaker_index}',
            }

def add_marker(segment: typing.Sequence, has_speakers:bool=False): -> Marker

    if speaker:
        speaker_index = int(segment['speaker_label'].split('_')[-1])

        return Marker(
                speaker=add_speaker(speaker_index=speaker_index),
                start_time = segment['start_time'],
                end_time = segment['end_time'],
        )

    else:

        return Marker(
                start_time = items_segment[0]['start_time']
                end_time = items_segment[-1]
                )


    return Marker


def from_amazon_job(job_name)
"""Create a Job Object based on the TranscriptiobJobName"""
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        return from_amazon_uri(job['Transcript']['TranscriptFileUri'])

def from_amazon_uri(uri)
"""Create a Job Object based on the TranscriptFileUri"""
        response = requests.get(job_uri)
        response.raise_for_status()
        transcription = response.json()
        name = transcription['jobName']
        base_text = transcription['results']['transcripts'][0]['transcript']

        if 'speaker_labels' in transcription['results']:
            labels = transcription['results']['speaker_labels']
            speakers = [add_speaker(x) for x in range(labels['speakers'])]
            markers = [add_marker(x, has_speakers=True) for x in labels['segments']]

        else:
            speakers = []
            items_segments = itertools.split_when(
                segment, lambda x:x['type']=='punctuation',
            )
            markers = [add_marker(x), for x in items_segments]

        return Job(
                base_text=base_text
                name=name,
                _transcription = transcription,
                speakers = speakers
                )
