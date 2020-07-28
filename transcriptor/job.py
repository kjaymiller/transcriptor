from transcriptor.alternatives import Alternative
from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import time
import logging
import typing
import more_itertools

def get_base_strftime(timestamp: float, time_format: str):
    """converts float to strftime using gmtime"""
    return time.strftime(time_format, time.gmtime(timestamp))

def mil_format(number: float, separator: str) -> str:
    """Given a Float from a timestap return the milisecond value"""
    decimal_point = str(number).split('.')[-1]
    return f'{separator}{decimal_point}0' # Amazon Transcribe Floats to the Hundreths Position


class Job:
    def __init__(
            self,
            name: str,
            base_text: str,
            markers: typing.List[Marker],
            transcription: typing.Dict[typing.Any, typing.Any],
            alternatives: typing.List[Alternative],
            speakers: typing.List[Speaker],
            ):

        self.name = name
        self.base_text = base_text # default transcription as text from rendering service
        self.speakers = speakers
        self.markers = []
        for marker in markers:
            speaker = None
            if marker['speaker']:
                for x, s in enumerate(self.speakers):
                    if s.base_name == marker['speaker']:
                        speaker = self.speakers[x]
                        break

            m = Marker(
                    speaker=speaker,
                    start_time=marker['start_time'],
                    end_time=marker['end_time'],
                    )

            self.markers.append(m)

        self.transcription = transcription # original transcription object pre-processed
        self.alternatives = alternatives

    def get_text_at_marker(self, marker) -> str:
        """Given a marker index, return the text. Formatted for that object"""
        marker_alternatives = []

        for item in self.alternatives:

            # punctuation items do not have start/end times
            if marker_alternatives and item._type == 'punctuation':
                marker_alternatives.append(item.content)

            elif item.start_time >= marker.start_time and item.end_time <= marker.end_time:

                # Add space if not the first pronunciation
                if marker_alternatives:
                    content = f' {item.content}'

                else:
                    content = item.content

                marker_alternatives.append(content)

            elif item.end_time > marker.end_time:
                break # to stop processing once you have left the range.

        return ''.join(marker_alternatives)

    @property
    def transcript(
            self, separator: str='\n\n', text_separator: str=':\n\n',
            has_speaker: bool=True, has_timestamp: bool=True,
            time_format="%H:%M:%S",
            ) -> str:

        transcription_text = []

        for marker in self.markers:
            text = self.get_text_at_marker(marker)
            speaker = ''
            start_time = ''

            if has_speaker and marker.speaker:
                speaker = marker.speaker.label + ' '

            if has_timestamp:
                start_time = get_base_strftime(
                        marker.start_time,
                        time_format=time_format,
                        )

            transcription_text.append(
                f'{speaker}{start_time}{text_separator}{text}',
                )

        return separator.join(transcription_text)

    @property
    def srt(self, has_speaker: bool=True) -> str:
        """Creates transcription file in srt format"""

        time_format="%H:%M:%S"
        separator: str='\n\n'
        transcription_text = []

        for index, marker in enumerate(self.markers, start=1):
            text = self.get_text_at_marker(marker)
            speaker = ''
            start_time = ''
            end_time = ''

            if has_speaker and marker.speaker:
                speaker = f'>> {marker.speaker.label}: '

            start_time = get_base_strftime(
                    marker.start_time,
                    time_format=time_format) + mil_format(marker.start_time,
                            separator=',')

            end_time = get_base_strftime(
                    marker.end_time,
                    time_format=time_format) + mil_format(marker.end_time,
                            separator=',')

            transcription_text.append(
                f'{index}\n{start_time} --> {end_time}\n{speaker}{text}',
                )

        return separator.join(transcription_text)

    @property
    def sbv(self, has_speaker: bool=True) -> str:
        """Creates transcription file in srt format"""

        time_format="%H:%M:%S"
        separator: str='\n\n'
        transcription_text = []

        for marker in self.markers:
            text = self.get_text_at_marker(marker)
            speaker = ''
            start_time = ''
            end_time = ''

            if has_speaker and marker.speaker:
                speaker = f'>> {marker.speaker.label}: '

            start_time = get_base_strftime(
                    marker.start_time,
                    time_format=time_format) + mil_format(marker.start_time,
                            separator='.')

            end_time = get_base_strftime(
                    marker.end_time,
                    time_format=time_format) + mil_format(marker.end_time,
                            separator='.')

            transcription_text.append(
                f'{start_time},{end_time}\n{speaker}{text}',
                )

        return separator.join(transcription_text)
