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
        self.alternatives = alternatives

    def text_at_marker(self, marker_index: int, separator: str=":\n") -> str:
        marker = sorted(self.markers, key=lambda x: x.start_time)[marker_index]
        marker_alternatives = []

        for item in self.alternatives:
            if marker_alternatives and item._type == 'punctuation':
                marker_alternatives.append(item.content)
                continue

            if item.start_time >= marker.start_time and item.end_time <= marker.end_time:
                marker_alternatives.append(item.content)
                continue

            elif item.end_time > marker.end_time:
                logging.warning(item.__dict__)
                break # to stop processing once you have left the range.

        if marker.speaker:
            marker_text = f'{marker.speaker} {marker.start_time}:'

        else:
            marker_text = str(marker.start_time)

        text = (' ').join(marker_alternatives)
        return f'{marker_text}{separator}{text}'


    def as_text(self, separator: str='\n\n', marker_separator:str=':\n'):
        text = [self.text_at_marker(x[0], separator=marker_separator) for x in enumerate(self.markers)]
        return separator.join(text)
