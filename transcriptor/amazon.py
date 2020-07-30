from .job import Job
from .markers import Marker
from .speakers import Speaker
from .alternatives import Alternative

from datetime import timedelta

import boto3
import more_itertools
import requests
import typing

transcribe = boto3.client('transcribe')

def text_in_range(segments, start_time, end_time):
    content = ''
    in_range = False

    for index, segment in enumerate(segments):
        if segment['type'] == 'punctuation':

            if in_range == True:
                content += segment['alternatives'][0]['content']

            else:
                continue

        elif float(segment['end_time']) <= float(end_time):

            if float(segment['start_time']) >= float(start_time):
                in_range = True
                content += " " + segment['alternatives'][0]['content']

        else:
            return content.strip()


def add_speaker(speaker_index: int) -> Speaker:
    """Create a speaker object from one of the labels in results['speaker_labels']"""
    return Speaker(
            base_name=f'spk_{speaker_index}',
            )


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
    markers = []
    segments = transcription['results']['items']

    if 'speaker_labels' in transcription['results']:
        labels = transcription['results']['speaker_labels']
        speakers = [add_speaker(x) for x in range(labels['speakers'])]

        for segment in labels['segments']:
            start_time=segment['start_time']
            end_time=segment['end_time']
            speaker=[x for x in speakers if x.base_name == segment['speaker_label']][0]
            content = text_in_range(
                    segments,
                    start_time=start_time,
                    end_time=end_time,
                    )
            marker = Marker(
                    start_time = timedelta(seconds=float(start_time)),
                    end_time = timedelta(seconds=float(end_time)),
                    content = content,
                    speaker = speaker
                    )
            markers.append(marker)

    else:
        speakers = []

        items_segments = more_itertools.split_when(
            segments, lambda x,y: x['alternatives'][0]['content'] in ['.', '?', '!'],
        )

        for index, item in enumerate(items_segments):
            start_time = timedelta(seconds=float(item[0]['start_time']))
            end_time = timedelta(seconds=float(item[-2]['end_time']))
            content = ''

            for word_block in item:
                if word_block['type'] == 'punctuation':
                    content += word_block['alternatives'][0]['content']
                else:
                    content += " " + word_block['alternatives'][0]['content']

            marker = Marker(start_time=start_time, end_time=end_time,
                    content=content)
            markers.append(marker)

    return Job.from_amazon(
            base_text = transcription['results']['transcripts'][0]['transcript'],
            name = transcription['jobName'],
            transcription=transcription,
            speakers = speakers,
            markers = markers,
            )
