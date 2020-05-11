from transcriptor.speakers import Speaker
from transcriptor.markers import Marker

import logging
import typing
import more_itertools

class Job:
    def __init__(
            self,
            name: str,
            base_text: str,
            markers: typing.List,
            transcription: typing.Dict,
            alternatives: typing.List,
            speakers: typing.List,
            ):

        self.name = name
        self.base_text = base_text
        self.markers = markers
        self.transcription = transcription
        self.speakers = speakers
        self.alternatives = sorted(alternatives, key=lambda x: x.start_time)

    def text_at_marker(self, marker_index: int) -> str:
        marker = self.markers[marker_index]
        marker_text = []

        for item in self.alternatives:

            if item.start_time >= marker.start_time and item.end_time <= marker.end_time:
                marker_text.append(item.content)

            elif item.end_time > marker.end_time:
                    logging.warning(item.__dict__)
                    break # to stop processing once you have left the range.

        return (' ').join(marker_text)
