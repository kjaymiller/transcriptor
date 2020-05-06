import boto3
import uuid

client = boto3.client('transcribe')

class Amazon:

    def __init__(self, **kwargs):
        self.output_encryption_kms_key_id =
                kwargs.get('output_encryption_kms_key_id', uuid.uuid4)

    def start_transcription_job(
            self, job, vocabulary=None, vocabulary_filter=None
            ):
        """Wrapper for the boto3 start_transcription_job method.
Takes a transcription job and returns the transcription job"""

        transcription_job_name = Job.key
        language_code = Job.language
        media_format = Job.media_format
        media = {'MediaFileUri': Job.uri}
        media_sample_rate_hertz = Job.sample_rate # I have never modified this.
        output_bucket_name = self.output_bucket
        output_encryption_kms_key_id = self.output_encryption_id
        settings = {}
                'show_speaker_labels': Job.has_speakers,
                'max_speaker_labels': len(Job.speakers),
                'channel_identification': Job.channel_identification,
                }

        # Add Vocabulary Settings if included
        if vocabulary:
            settings['Vocabulary'] = Vocabulary.name


        if vocabulary_filter:
            settings.update{
                    'VocabularyFilterName': vocabulary_filter.name,
                    'VocabularyFilterMethod': vocabulary_filter.filter_method,
                    }
