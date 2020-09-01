from .job import Job
from .markers import Marker
from .speakers import Speaker
from .alternatives import Alternative

from datetime import timedelta
from pathlib import Path
from slugify import slugify

import boto3
import more_itertools
import requests
import logging
import os
import typing

storage = boto3.client('s3')
transcribe = boto3.client('transcribe')

def to_key(path_name:str):
        valid_keytypes = ['.mp3', '.mp4', '.wav', '.flac']
        path = Path(path_name)
        path_suffix =  path.suffix

        if path_suffix.lower() not in valid_keytypes:
            msg = "The file that you entered is not a valid filetype. You \
may experience issues with submitting a transcription."
            logging.warning(msg)

        slug_path = slugify(str(path).split(path_suffix)[0])
        return slug_path + path_suffix


class AmazonJob(Job):
    def __init__(
            self,
            filepath: typing.Optional[str] = '',
            base_text: typing.Optional[str] = '',
            markers: typing.List[typing.Optional[Marker]] = [],
            bucket: typing.Optional[str]=None,
            started: typing.Optional[str]=None,
            transcription: typing.Dict[typing.Any, typing.Any] = {},
            alternatives: typing.List[Alternative] = [],
            speakers: typing.List[Speaker] = [],
            ):

        self.bucket = bucket
        self.base_text = base_text # default transcription as text from rendering service
        self.speakers = speakers
        self.markers = markers
        self.transcription = transcription # original transcription object pre-processed
        self.alternatives = alternatives

        if filepath:
            self.key = to_key(filepath)
            self.filepath = Path(filepath)

        else:
            self.key = ''

        self.name = self.key

        if started:
            self._status = status

        else:
            self._status = 'NOT STARTED'


    @property
    def status(self):
        if self._status in ['COMPLETED', 'NOT STARTED']:
            return self._status

        job = transcribe.get_transcription_job(TranscriptionJobName=self.key)
        status = job['TranscriptionJob']['TranscriptionJobStatus']

        if status == 'COMPLETED':
            self._status = status

        if status != 'IN_PROGESS':
            self._status = status

        return status

    def upload_audio_file(self, filename):
        """Loads file to amazon s3 location"""
        return storage.upload_file(str(self.filepath), Bucket=self.bucket,
                Key=self.key)

    def start(self,
        language: str='en-US',
        speakers: int=0,
        storage=storage,
        transcribe=transcribe,
        ):

        audio_file = self.upload_audio_file(self.filepath)

        transcribe_job_uri = f"{storage.meta.endpoint_url}/{self.bucket}/{self.key}"
        print(transcribe_job_uri)

        if speakers:
            settings = {
                "ShowSpeakerLabels": True,
                "MaxSpeakerLabels": speakers,
                }
        else:
            settings = {}

        transcribe.start_transcription_job(
            TranscriptionJobName=self.key,
            Media={"MediaFileUri": transcribe_job_uri},
            MediaFormat=Path(self.filepath).suffix[1:],
            LanguageCode=language,
            Settings=settings,
        )

        # reset status so that it will check for it
        self._status = ''
        return self.status

    @staticmethod
    def from_job(job_name: str) -> Job:
        """Create a Job Object based on the TranscriptiobJobName"""
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        return AmazonJob.from_uri(job['TranscriptionJob']['Transcript']['TranscriptFileUri'])

    @staticmethod
    def from_uri(uri:str) -> Job:
        """Create a Job Object based on the TranscriptFileUri"""
        response = requests.get(uri)
        response.raise_for_status()

        return AmazonJob.from_json(response.json())

    def build(self) -> Job:
        """Create a Job Object when given an Amazon JSON Object"""
        job = transcribe.get_transcription_job(TranscriptionJobName=self.key)
        uri = job['TranscriptionJob']['Transcript']['TranscriptFileUri']
        response = requests.get(uri)
        response.raise_for_status()

        transcription = response.json()
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

        # add alternatives
        alternatives = []
        for item in segments:

            if item['type'] == 'pronunciation':

                for alt in item['alternatives']:
                    alternatives.append(Alternative(
                        start_time = item['start_time'],
                        content = alt['content'],
                        confidence = alt['confidence'],
                        tag = 'orignal',
                        _type = 'pronunciation',
                        ))

        self.base_text = transcription['results']['transcripts'][0]['transcript']
        self.transcription=transcription
        self.speakers = speakers
        self.markers = markers
        self.alternatives = alternatives


    @classmethod
    def from_json(cls, transcription) -> Job:
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

        # add alternatives
        alternatives = []
        for item in segments:

            if item['type'] == 'pronunciation':

                for alt in item['alternatives']:
                    alternatives.append(Alternative(
                        start_time = item['start_time'],
                        content = alt['content'],
                        confidence = alt['confidence'],
                        tag = 'orignal',
                        _type = 'pronunciation',
                        ))

        return cls(
                base_text = transcription['results']['transcripts'][0]['transcript'],
                key = transcription['jobName'],
                transcription=transcription,
                speakers = speakers,
                markers = markers,
                alternatives = alternatives,
                )

## Download Jobs
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
