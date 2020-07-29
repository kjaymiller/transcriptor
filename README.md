![Transcriptor Logo](https://s3-us-west-2.amazonaws.com/kjaymiller/images/Transcriptor%20Logo%20V1.1.png)
# Transcriptor
## A transcription service wrapper that makes it easier to work with transcriptions.

Transcription services provide a cost-effective way to add accessibility to
your audio and video, but they are often a challenge to integrate into your system.

**Transcriptor aims to make working with transcriptions easier.**

Transcriptor looks at transcription objects as a class.

### Features:

- An object-oriented approach to Transcriptions, Markers, and Speakers
- Nondestructive manipulation of text and references.

## Installation
Install transcriptor using pip.

`pip install transcriptor`


## Quickstart
Transcriptor currently does not support automated transcription upload, but it
supports creating **READABLE** Transcription `Job` objects from their output.

Importing transcription JSON Output from AWS Transcribe

Because transcriptor is designed to wrap around AWS Transcribe if you have
configured your environment with information for AWS, you can directly convert
AWS Transcribe jobs to Transcriptor Jobs with the `amazon.from_job()` method.

```python
from transcriptor import amazon

amazon.from(job="<TranscriptionJobName>")
```

Alternatively, you can load the object via the _TranscriptFileUri_
(`amazon.from_uri()`) or the JSON object directly (`amazon.from_json()`).

## Supported Services

- Amazon Transcribe (boto3)

## Planned Support For

- Google Speech-To-Text

## Sponsors
This and much of the work that I do is made possible by those that sponsor me
on github.

### Sponsors at the $20/month and higher Level
- [Brian Douglas](https://github.com/bdougie)
- [Anthony Shaw](https://github.com/tonybaloney)
- [Carol Willing](https://github.com/willingc)

Thank you to them and all of those that continue to support this project!

[**Sponsor this Project**](https://github.com/sponsors/kjaymiller)
