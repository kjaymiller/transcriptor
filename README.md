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

Transcriptor currently supports transcription upload and 
creating a **READABLE Transcription Job Object** from their output.

### Importing Transcriptions from AWS Transcribe

```python
from transcriptor import amazon, AmazonJob

job = AmazonJob(filepath='<filepath>', bucket='<bucket_name>', )
job.start()
# After Some Time
job.status() # If it says COMPLETED
job.build()
```

Alternatively, you can load the object via the _TranscriptFileUri_
(`AmazonJob.from_uri()`) or the JSON object directly (`AmazonJob.from_json()`).

A loaded Transcription Job from AWS Transcribe will give you access to `Markers`, `Speakers`
(if included), the provided `Alternatives`. You also have the original job
object that you can interact with.

### Importing from an SubRip Subtitle (SRT)

Text Transcriptions from the Web can be very unique in style, but the most
common format is that of at srt file.

You can load an srt file into transcriptor and use that to interact with the
individual markers.

```python
from transcriptor import Job

amazon.from_srt('FILENAME.srt')
```

A loaded Transcription Job from srt files will make `Markers`.

These markers are given in order as a list. This gives you the ability to
modify a single Marker or iterate your changes across a range or all of the
Marker objects.

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
