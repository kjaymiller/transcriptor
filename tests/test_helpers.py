import pytest
from transcriptor.helpers import text_in_range


@pytest.fixture()
def segments():
    segment = [
            {
                "start_time":0.000,
                "end_time": 1.0000,
                "type":"pronunciation",
                "alternatives": [{
                    "confidence": 1.0,
                    "content": "Once",
                    }],
                
            },
            {
                "start_time":1.000,
                "end_time": 2.0000,
                "type":"pronunciation",
                "alternatives": [{
                    "confidence": 1.0,
                    "content": "Upon"
                    }],
            },
            {
                "start_time":3.000,
                "end_time": 4.0000,
                "type":"pronunciation",
                "alternatives": [{
                    "confidence": 0.0,
                    "content": "b"
                    },
                    {
                    "confidence": 0.4,
                    "content": "A"
                    },
                    ],
            },
            {
                "start_time":4.000,
                "end_time": 6.0000,
                "type": "punctuation",
                "alternatives": [{
                    "confidence": 1.0,
                    "content": "."
                    }],
            },
        ]
    return segment

def test_text_in_range_gets_only_text_in_range(segments):
    """Given a segment text_in_range returns the text between the 
    start/stop times"""

    # Test that only the 2 of the segments are returned
    target_start_time = 1.3
    target_end_time = 3.5

    test_text = text_in_range(segments, target_start_time, target_end_time)
    assert test_text == "Upon A"


def test_text_in_range_doesnt_add_space_for_punctuation(segments):
    """Punctuation should not have a space before it.""" 

    target_start_time = 2.3
    target_end_time = 7.5

    test_text = text_in_range(segments, target_start_time, target_end_time)
    assert test_text == "A."

