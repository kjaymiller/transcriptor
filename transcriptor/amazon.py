from .job import Job
from .markers import Marker 
from .alternatives import Alternative
from .helpers import text_in_range
from .speakers import Speaker

from datetime import timedelta
from pathlib import Path
from slugify import slugify

import boto3
import dataclasses
import more_itertools
import httpx
import logging
import os
import typing
import json

storage = boto3.client("s3")
transcribe = boto3.client("transcribe")

class AmazonEnv():
    def __init__(
    self,
    asr_Output: typing.Optional[dict]=None,
    key: typing.Optional[str]=None,
    audio_file: typing.Optional[str]=None,
    bucket: typing.Optional[str]=None,
    is_uploaded: bool=True,
    ):

        self.is_uploaded = False

        if bucket:
            self.bucket = bucket

        if audio_file:
            self.audio_file = Path(audio_file)

            if not key:
                key = slugify(str(audio_file))

        check_key = slugify(key) # coerce valid naming structure

        if key != check_key:
            logging.warning(f'invalid-{key=}. Will use {check_key} instead.')

        self.key = check_key


    def upload_audio_file(self, **kwargs):
        """Loads file to amazon s3 location. 
        This is a convenience wrapper for storage.upload_file
        """
        storage.upload_file(str(self.audio_file), Bucket=self.bucket, Key=self.key, **kwargs)
        self.is_uploaded=True


    def start_transcription(
        self,
        *,
        language:str = 'en-US',
        vocabulary: typing.Optional[str]=None,
        speaker_count: int = 0,
    ):
        """Optionally upload the file and start the transcription job.
        This is a convenient wrapper for transcription.start_tranascription_job
        """

        if not self.is_uploaded:
            audio_file = self.upload_audio_file()

        transcribe_job_uri = f"{storage.meta.endpoint_url}/{self.bucket}/{self.key}"
        settings = {}

        if speaker_count > 0:
            settings["ShowSpeakerLabels"] = True
            settings["MaxSpeakerLabels"] = speaker_count

        if vocabulary:
            settings["VocabularyName"] = vocabulary

        return transcribe.start_transcription_job(
            TranscriptionJobName=self.key,
            Media={"MediaFileUri": transcribe_job_uri},
            MediaFormat=Path(self.audio_file).suffix[1:],
            LanguageCode=language,
            Settings=settings,
        )

    @staticmethod
    def from_job(job_name: str) -> Job:
        """Create a Job Object based on the TranscriptiobJobName"""
        job = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        return AmazonEnv.from_uri(
            job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )

    @staticmethod
    def from_uri(uri: str) -> Job:
        """Create a Job Object based on the TranscriptFileUri"""
        response = httpx.get(uri)
        return AmazonEnv.from_json(response.json())

    def build(
            self,
            *,
            split_at:typing.List[str]=['.', '?', '!'],
            ignore_speakers:bool=False
            ) -> Job:
        """
        Create a Job Object when given an Amazon JSON Object
        
        Parameters
        ----------
        split_at: list
            punctuation objects to split for markers
        ignore_speakers: bool
        """
        pass

    @classmethod
    def from_json(cls, json_file) -> Job:
        """Create a Job Object when given an Amazon JSON Object"""

        results = json_file['results']

        if "speaker_labels" in results:
            labels = json_file["results"]["speaker_labels"]
            segments = labels["segments"]
            
        else:
            segment_content = more_itertools.split_when(
                json_file['results']['items'],
                lambda x: x['type'] == "pronunciation"
            )
            segments=[]

            for segment in segment_content:
                segments.append({
                    'start_time': float(item[0]["start_time"]),
                    'end_time': float(item[-1]["end_time"]),
                    'speaker': None,
                    })



def from_transcription_jobs(**kwargs):
        """Get a list of transcription jobs and generate a job object for each one
        """

        for job in transcribe.list_transcription_jobs(**kwargs)["TranscriptionJobSummaries"]:
            yield AmazonEnv.from_job(job["TranscriptionJobName"])
