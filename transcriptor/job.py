from .alternatives import Alternative
from .tools import (
    adjust_microseconds,
    timedelta_from_str,
    timedelta_to_dict,
)
from .speakers import Speaker
from .markers import Marker

from pathlib import Path
from datetime import timedelta
import re
import string
import time
import logging
import typing
import more_itertools


class Job:
    """Job objects are the foundation of transcriptor. A job holds the markers, speakers, alternatives, and outputs for a transcription"""

    @classmethod
    def from_srt(cls, filepath: str, skip_checks: bool=False):
        """builds a Job object from a srt file
        Parameters
        ----------
        filepath: Path-like object
            the file to be parsed into a Job object
        skip_checks: bool, optional
            if true time-inconsistencies will not raise an error

        Returns
        -------
        Job

        Raises
        ------
        ValueError: OverLappingStartTime
            if skip_checks is False, the start_time of an index marker must
            be later than the end_time of the previous marker.
        """
        new_job = cls()
        new_job.name = Path(filepath).name
        base_content = Path(filepath).read_text()
        new_job.base_text = (
            base_content  # default transcription as text from rendering service
        )
        new_job.transcription = Path(
            filepath
        )  # original transcription object pre-processed

        # build_markers
        marker_text = re.split("\n{2,}", base_content)
        markers = []
        alternatives = []

        for index, marker in enumerate(marker_text):
            marker_segments = marker.strip().split("\n", maxsplit=2)

            if len(marker_segments) != 3:
                raise ValueError(f"{filepath} has an invalid {marker_segments=}.")

            _, timestamps, content = [x for x in marker_segments]
            start_time, end_time = timestamps.split(" --> ")
            start_time = timedelta_from_str(start_time)

            if index != 0 and skip_checks == False:
                if start_time < (previous_entry := markers[index - 1]).end_time:
                    raise ValueError(
                        f"OverLappingStartTime: {filepath.name} index - {index+1} start_time \
{start_time=} starts before {previous_entry.end_time=}"
                    )

            end_time = timedelta_from_str(end_time)

            markers.append(
                Marker(
                    start_time=start_time,
                    end_time=end_time,
                    content=content,
                )
            )

            for word in re.split(r" +|\n+", content.strip()):
                results = []

                if word.strip() in string.punctuation:
                    NewPunct = Alternative(
                        content=word,
                        confidence=0.0,
                        _type="punctuation",
                    )
                    results.append(NewPunct)
                    word = word

                NewAlternative = Alternative(
                    content=word,
                    confidence=0.0,
                    _type="pronunciation",
                )
                results.insert(0, NewAlternative)
                alternatives.extend(results)

        new_job.markers = markers
        new_job.alternatives = alternatives
        return new_job

    def to_text(
        self,
        separator: str = "\n\n",
        text_separator: str = ":\n\n",
        has_speaker: bool = True,
        has_timestamp: bool = True,
    ) -> str:

        transcription_text = []

        for marker in self.markers:
            text = marker.content
            speaker = ""
            start_time = ""

            if has_speaker and marker.speaker:
                speaker = marker.speaker.label + " "

            if has_timestamp:
                time_dict = timedelta_to_dict(
                    marker.start_time,
                )
                hours, minutes = [
                    str(x).zfill(2) for x in [time_dict["hours"], time_dict["minutes"]]
                ]
                _, seconds = divmod(marker.start_time.seconds, 60)
                seconds = str(int(seconds)).zfill(2)

                start_time = f"{hours}:{minutes}:{seconds}"

            transcription_text.append(
                f"{speaker}{start_time}{text_separator}{text}",
            )

        return separator.join(transcription_text)

    @property
    def srt(self) -> str:
        """Creates transcription file in srt format"""

        separator: str = "\n\n"
        transcription_text = []

        for index, marker in enumerate(self.markers, start=1):
            text = marker.content.strip()

            st = timedelta_to_dict(marker.start_time)
            st_hours, st_minutes = [
                str(x).zfill(2) for x in [st["hours"], st["minutes"]]
            ]
            st_seconds = adjust_microseconds(marker.start_time, separator=",")
            start_time = f"{st_hours}:{st_minutes}:{st_seconds}"

            et = timedelta_to_dict(marker.start_time)
            et_hours, et_minutes = [
                str(x).zfill(2) for x in [et["hours"], et["minutes"]]
            ]
            et_seconds = adjust_microseconds(marker.end_time, separator=",")
            end_time = f"{et_hours}:{et_minutes}:{et_seconds}"

            transcription_text.append(
                f"{index}\n{start_time} --> {end_time}\n{text}",
            )

        return separator.join(transcription_text)

    def load_edit(self, filepath: str):
        "builds a Job object from a srt file"
        base_content = Path(filepath).read_text()
        self.base_text = (
            base_content  # default transcription as text from rendering service
        )
        self.transcription = Path(
            filepath
        )  # original transcription object pre-processed

        # build_markers
        marker_text = base_content.split("\n\n")
        markers = []
        alternatives = []

        for index, marker in enumerate(marker_text):
            logging.debug(marker)
            _, timestamps, content = marker.split("\n")
            start_time, end_time = timestamps.split(" --> ")
            start_time = timedelta_from_str(start_time)

            if index != 0:
                if start_time < (previous_entry := markers[index - 1]).end_time:
                    raise ValueError(
                        f"OverLappingStartTime: {filepath.name} index - {index+1} start_time \
{start_time=} starts before {previous_entry.end_time=}"
                    )

            end_time = timedelta_from_str(end_time)

            markers.append(
                Marker(
                    start_time=start_time,
                    end_time=end_time,
                    content=content,
                )
            )

            for word in re.split(r" |\n", content.strip()):
                results = []

                word = word.strip("".join(string.punctuation))

                NewAlternative = Alternative(
                    content=word.strip(),
                    confidence=1.0,
                    _type="pronunciation",
                    tag="edit",
                    region_start_time=start_time.total_seconds(),
                )

                self.alternatives.append(NewAlternative)

        self.markers = markers
