from transcriptor.job import Job
import pytest

@pytest.fixture()
def tmp_file_data():
    return """
00:00:00,000 --> 00:00:02,123
This, is a test.

2
00:00:03,000 --> 00:00:4,456
Another test for me."""

def test_job_from_srt_creates_markers(tmp_file_data, tmp_path):
    test_file = tmp_path / 'test_file.srt'
    test_file.write_text(tmp_file_data)
    newFile = Job.from_srt(test_file)
    assert len(newFile.markers) == 2


def test_job_from_srt_creates_alternatives(tmp_file_data, tmp_path):
    test_file = tmp_path / 'test_file.srt'
    test_file.write_text(tmp_file_data)
    newJob = Job.from_srt(test_file)
    assert len(newJob.alternatives) == 11


def test_job_puncuations(tmp_file_data, tmp_path):
    test_file = tmp_path / 'test_file.srt'
    test_file.write_text(tmp_file_data)
    newFile = Job.from_srt(test_file)
    punctuations = [x for x in newFile.alternatives if x._type=='punctuation']
    assert len(punctuations) == 3
