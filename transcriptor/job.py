from transcriptor.alternatives import Alternative
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
            markers: typing.List[Marker],
            transcription: typing.Dict[typing.Any, typing.Any],
            alternatives: typing.List[Alternative],
            speakers: typing.List[Speaker],
            ):

        self.name = name
        self.base_text = base_text # default transcription as text from rendering service
        self.markers = markers
        self.transcription = transcription # original transcription object pre-processed
        self.speakers = speakers
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


    def as_text(self, separator: str='\n\n', text_separator: str=':\n\n',
            has_speaker: bool=True, has_timestamp: bool=True) -> str:
        transcription_text = []

        for marker in self.markers:
            text = self.get_text_at_marker(marker)
            speaker = ''
            start_time = ''

            if has_speaker and marker.speaker:
                speaker = marker.speaker.label + ' '

            if has_timestamp:
                start_time = marker.start_time

            transcription_text.append(
                f'{speaker}{start_time}{text_separator}{text}',
                )


        return separator.join(transcription_text)
