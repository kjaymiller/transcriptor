from job import Job

import boto3
import requests

transcribe = boto3.client('transcribe')

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

        if 'speaker_labels' in transcription['results']:
            labels = transcription['results']['speaker_labels']['speakers']
            speakers = [f'spk_{x}' for x in range(labels)]
        else:
            speakers = []

        return Job(
                name=name,
                _transcription = transcription,
                speakers = speakers
                )
