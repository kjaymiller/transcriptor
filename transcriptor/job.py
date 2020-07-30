from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

from pathlib import Path
from datetime import timedelta
import re
import time
import logging
import typing
import more_itertools

def adjust_microseconds(time_val: timedelta, separator='.') -> str:
    """Take the microseconds from a timedelta and return the first three values"""
    _, seconds = divmod(time_val.seconds, 60)
    return str(seconds).zfill(2) + separator + str(time_val.microseconds)[:3]


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
        time_float.total_seconds(), 60
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
            speakers: typing.List[Speaker],
            ):

        new_job = cls()
        new_job.name = name
        new_job.base_text = base_text # default transcription as text from rendering service
        new_job.speakers = speakers
        new_job.markers = markers
        new_job.transcription = transcription # original transcription object pre-processed
        return new_job

    @property
    def transcript(
            self, separator: str='\n\n', text_separator: str=':\n\n',
            has_speaker: bool=True, has_timestamp: bool=True,
            ) -> str:

        transcription_text = []

        for marker in self.markers:
            text = marker.content
            speaker = ''

            if has_speaker and marker.speaker:
                speaker = marker.speaker.label + ' '

            if has_timestamp:
                time_dict = convert_time_float(
                        marker.start_time,
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
    def srt(self) -> str:
        """Creates transcription file in srt format"""

        separator: str='\n\n'
        transcription_text = []

        for index, marker in enumerate(self.markers, start=1):
            text = marker.content

            st = convert_time_float(marker.start_time)
            st_hours, st_minutes = [str(x).zfill(2) for x in
                    [st['hours'],st['minutes']]]
            st_seconds = adjust_microseconds(marker.start_time, separator=',')
            start_time = f"{st_hours}:{st_minutes}:{st_seconds}"

            et = convert_time_float(marker.start_time)
            et_hours, et_minutes = [str(x).zfill(2) for x in
                    [et['hours'],et['minutes']]]
            et_seconds = adjust_microseconds(marker.end_time, separator=',')
            end_time = f"{et_hours}:{et_minutes}:{et_seconds}"

            transcription_text.append(
                f'{index}\n{start_time} --> {end_time}\n{text}',
                )

        return separator.join(transcription_text)
