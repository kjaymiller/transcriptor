from transcriptor.alternatives import Alternative
from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

from pathlib import Path
from datetime import timedelta
import re
import time
import logging
import typing
import more_itertools

def mil_format(number: float, separator: str) -> str:
    """Given a Float from a timestap return the milisecond value"""
    decimal_point = str(number).split('.')[-1]
    return f'{separator}{decimal_point}0' # Amazon Transcribe Floats to the Hundreths Position


def adjust_microseconds(time_val: str) -> str:
    """Take the microseconds string and convert it to milliseconds"""

    while len(time_val) < 6:
        time_val += "0"

    return int(time_val)

def timedelta_from_str(time_str:str) -> timedelta:
    time_splitter = r':'
    time_vals = re.split(time_splitter, time_str)
    time_vals[-1] = time_vals[-1].replace(',','.') # srt time = H:M:S,Mil

    return timedelta(
            hours=int(time_vals[0]),
            minutes=int(time_vals[1]),
            seconds=float(time_vals[2]),
            )

def convert_time_float(time_float: float) -> typing.Dict:
    """Convert the time float from output.json and create a dict"""
    minutes, seconds = divmod(
        time_float, 60
    )  # seconds will still have microseconds attached
    hours, minutes = divmod(minutes, 60)

    return {'hours': int(hours), 'minutes': int(minutes), 'seconds': seconds}

def time_delta_from_float(time_float: float) -> timedelta:
    """Convert the time float from output.json and create a timedelta"""
    return timedelta(seconds=time_float)

class Job:
    @classmethod
    def from_srt(cls, filepath: str):
        base_content = Path(filepath).read_text()
        new_job = cls()
        new_job.base_text = base_content # default transcription as text from rendering service
        new_job.transcription = Path(filepath) # original transcription object pre-processed

        # build_markers
        marker_text = base_content.split('\n\n')
        markers = []

        for index, marker in enumerate(marker_text):
            _, timestamps, content = marker.split('\n')
            start_time, end_time = timestamps.split(' --> ')
            start_time = timedelta_from_str(start_time)

            if index != 0:
                if start_time < (previous_entry:=markers[index-1]).end_time:
                    raise ValueError(f'OverLappingStartTime: index - {index+1} start_time \
{start_time=} starts before {previous_entry.end_time=}')

            end_time = timedelta_from_str(end_time)

            markers.append(
                    Marker(
                        start_time=start_time,
                        end_time=end_time,
                        content=content,
                        ))
        new_job.markers = markers
        return new_job

    @classmethod
    def from_amazon(
            cls,
            name: str,
            base_text: str,
            markers: typing.List[Marker],
            transcription: typing.Dict[typing.Any, typing.Any],
            alternatives: typing.List[Alternative],
            speakers: typing.List[Speaker],
            ):

        new_job = cls()
        new_job.name = name
        new_job.base_text = base_text # default transcription as text from rendering service
        new_job.speakers = speakers

        markers = []

        for marker in markers:
            speaker = None
            if marker['speaker']:
                for x, s in enumerate(new_job.speakers):
                    if s.base_name == marker['speaker']:
                        speaker = new_job.speakers[x]
                        break

            m = Marker(
                    speaker=speaker,
                    start_time=marker['start_time'],
                    end_time=marker['end_time'],
                    )

            markers.append(m)

        new_job.markers = markers
        new_job.transcription = transcription # original transcription object pre-processed
        new_job.alternatives = alternatives
        return new_job

    def get_text_at_marker(self, marker) -> str:
        """Given a marker index, return the text. Formatted for that object"""

        if marker.content:
            return marker.content

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
            ) -> str:

        transcription_text = []

        for marker in self.markers:
            text = self.get_text_at_marker(marker)
            speaker = ''

            if has_speaker and marker.speaker:
                speaker = marker.speaker.label + ' '

            if has_timestamp:
                time_dict = convert_time_float(
                        marker.start_time.total_seconds(),
                        )
                hours, minutes = [str(x).zfill(2) for x in
                    [time_dict['hours'],time_dict['minutes']]]
                _, seconds = divmod(marker.start_time.seconds, 60)
                seconds = str(int(seconds)).zfill(2)

                start_time = f"{hours}:{minutes}:{seconds}"

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

            if has_speaker and marker.speaker:
                speaker = f'[{marker.speaker.label}]:'

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
