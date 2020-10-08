from .job import Job
from .markers import Marker, gen_markers
from .alternatives import Alternative, gen_alternatives
from .helpers import text_in_range

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

        else:
            self.bucket = os.environ.get('AWS_BUCKET', None)

        if audio_file:
            self.audio_file = Path(audio_file)

            if not key:
                key = slugify(str(audio_file))

        check_key = slugify(key) # coerce valid naming structure

        if key != check_key:
            logging.warning(f'invalid-{key=}. Will use {check_key} instead.')

        self.key = check_key



    def upload_audio_file(self):
        """Loads file to amazon s3 location. 
        This is a convenience wrapper for storage.upload_file
        """
        return storage.upload_file(str(self.audio_file), Bucket=self.bucket, Key=self.key)


    def start_transcription(
        self,
        *,
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
        return AmazonJob.from_uri(
            job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        )

    @staticmethod
    def from_uri(uri: str) -> Job:
        """Create a Job Object based on the TranscriptFileUri"""
        response = httpx.get(uri)
        return AmazonJob.from_json(response.json())

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
        split_at: List
            punctuation objects to split for markers

        Returns
        -------
        Job
        """
        job = transcribe.get_transcription_job(TranscriptionJobName=self.key)
        uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        response = httpx.get(uri)

        transcription = response.json()
        markers = []
        segments = transcription["results"]["items"]

        if "speaker_labels" in transcription["results"]:
            labels = transcription["results"]["speaker_labels"]
            speakers = {x: Speaker(base_name=x) for x in range(labels["speakers"])}

            for segment in labels["segments"]:
                start_time = segment["start_time"]
                end_time = segment["end_time"]

                # get the speaker of the label
                speaker = speakers[segment['speaker_label']]
                content = text_in_range(
                    segments,
                    start_time=start_time,
                    end_time=end_time,
                )

        else: # No speakers provided
            speakers = {}
            items_segments = list(more_itertools.split_when(
                segments,
                lambda x,_: x["alternatives"][0]["content"] in split_at
            ))

            logging.debug(items_segments)

            for index, item in enumerate(items_segments):
                start_time = timedelta(seconds=float(item[0]["start_time"]))
                end_time = timedelta(seconds=float(item[-2]["end_time"]))
                content = ""

                for word_block in item:
                    if word_block["type"] == "punctuation":
                        content += word_block["alternatives"][0]["content"]
                    else:
                        content += " " + word_block["alternatives"][0]["content"]

                marker = Marker(
                    start_time=start_time, end_time=end_time, content=content
                )
                markers.append(marker)

        # add alternatives
        alternatives = []
        for item in segments:

            if item["type"] == "pronunciation":

                for alt in item["alternatives"]:
                    alternatives.append(
                        Alternative(
                            start_time=item["start_time"],
                            content=alt["content"],
                            confidence=alt["confidence"],
                            tag="orignal",
                            _type="pronunciation",
                        )
                    )

        new_job = Job()
        new_job.base_text = transcription["results"]["transcripts"][0]["transcript"]
        new_job.transcription = transcription
        new_job.speakers = speakers
        new_job.markers = markers
        new_job.alternatives = alternatives
        
        return new_job

    @classmethod
    def from_json(cls, json_file) -> Job:
        """Create a Job Object when given an Amazon JSON Object"""

        results = json_file['results']

        if "speaker_labels" in results:
            labels = json_file["results"]["speaker_labels"]
            segments = labels["segments"]:
            
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

        return Job(
            base_text=results["transcripts"][0]["transcript"],
            key=json_file["jobName"],
            transcription=json_file,
            speakers=speakers,
            markers=gen_markers(segments),
            alternatives=gen_alternatives(results['items']),
        )


def from_transcription_jobs(**kwargs):
        """Get a list of transcription jobs and generate a job object for each one
        """

        for job in transcribe.list_transcription_jobs(**kwargs)["TranscriptionJobSummaries"]:
            yield AmazonEnv.from_job(job["TranscriptionJobName"])
