from datetime import timedelta
from dataclasses import dataclass
import typing

@dataclass
class Alternative:
    content: str
    confidence: float
    _type: str
    tag: typing.Optional[str] = None
    start_time: typing.Optional[str] = None
    region_start_time: typing.Optional[str] = None


    def find_alternates(self, job):
        """Checks for for marker in job where the alternative start_time
        exists. And returns all alternatives in the job with the tag edit
        belonging to that marker"""

        start_time = timedelta(seconds=float(self.start_time))

        for i, marker in enumerate(job.markers):

            if marker.start_time >= start_time:
                return job.markers[i-1]
