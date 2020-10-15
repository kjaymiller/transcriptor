from .alternatives import Alternative
from .tools import (
    str_to_timedelta,
    timedelta_from_str,
)
from .helpers import text_in_range
from .speakers import Speaker
from .markers import Marker
from .segments import Segment
from .speakers import Speaker

from pathlib import Path
from datetime import timedelta
import string
import time
import logging
import typing


class Job():
    """Job objects are the foundation of transcriptor. A job holds the markers, segments, speakers, alternatives, and outputs for a transcription"""

    def __init__(self,
            *, 
            markers: typing.Optional[typing.List[Marker]]=None,
            segments: typing.Optional[typing.List[Segment]]=None,
            speakers: typing.Optional[typing.List[Speaker]]=None,
            text: typing.Optional[str]=None,
            ):

        self.markers = markers
        self.segments = segments
        self.speakers = speakers
        self.text = text

    def _check_marker_content(self, marker):
        """checks given marker for content otherwise loads segments between the
        marker start and end times
        """

        if marker.content:
            return marker.content

        else:
            return text_in_range(
                    self.segments, 
                    start_time=marker.start_time,
                    end_time=marker.end_time,
                    )


    def _text_from_marker(self) -> typing.Generator:
        """Generate dictionaries of text for each Marker value"""
        markers = []

        for marker in self.markers:
            markers.append({
                "start_time": marker.start_time,
                "end_time": marker.end_time,
                "content": self._check_marker_content(marker),
                "speaker": marker.speaker if marker.speaker else '',
                })

        return markers


    def to_text(
        self,
        separator: str = "\n\n",
        text_separator: str = ":\n\n",
        disable_speakers: bool = False,
        disable_timestamp: bool = False,
    ) -> str:

        markers = list[self._text_from_marker()]

        lines = []

        for marker in markers:

            if disable_speakers:
                marker['speaker'] = ''

            if disable_timestamp:
                marker['start_time'] = ''

            lines.append(f"{speaker}{start_time}{text_separator}{content}")

        return separator.join(lines)
