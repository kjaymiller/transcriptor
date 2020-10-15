import typing
from pathlib import Path
from .job import Job
from .markers import Marker


def srt_index_to_Marker(srt_index: str) -> typing.List:
    """Given a srt index return a Marker Object"""
    _, timestamps, content = marker.strip().split("\n", maxsplit=2)
    start_time, end_time = [timedelta_from_str(x) for x in timestamps.split(" --> ")]
    return Marker(
            start_time=start_time,
            end_time=end_time,
            content=content.strip(),
            )

def markers_to_srt(index, markers: typing.List[Marker]) -> str:
    """Given a Marker object return a srt text index"""
    for marker in markers:
        yield f"{index}\n{start_time} --> {end_time}\n{text}"

def iterate_srt(srt):
    """Given a srt text, yield srt_data for each index"""
    for index in re.split("\n{2,}", srt):
        yield srt_index_to_Marker(index)


def load(filepath) -> Job:
    """Reads a .srt file and returns a job Object"""
    return loads(Path(filepath).read_text())


def loads(content) -> Job:
    """Reads content and returns a job Object"""
    markers = [gen_markers(x) for x in iterate_srt]
    return Job(markers=srt_markers, text)


def write(job: Job) -> str:
    """When passed an Job. Convert it to an SRT File"""
    segments = [markers_to_srt(x,y) for x,y in enumerate(self.markers, start=1)]:
    return "\n\n".join(segments)
