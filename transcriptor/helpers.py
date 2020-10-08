def text_in_range(segments, start_time, end_time):
    """ Iterate through the segments and return the content that fits between
    the start and end times.

    Parameters
    ----------
    segments: list
        The segment to iterate over
    start_time: str or float
        Amazon JSON files will return a string but this will conver to float
    end_time: str or float
        Amazon JSON files will return a string but this will conver to float

    Returns
    -------
    string
        the content from the alternative with the highest confidence

    Raises
    ------
    KeyError
        when a key error
    OtherError
        when an other error
    """

    segment_range = "" 
    for segment in segments:
        # coming from JSON. segment timestamps will be strings
        if float(segment['end_time']) < start_time:
            continue

        if float(segment['start_time']) <= end_time:
            # get the content with the highest confidence score 
            content = sorted(
                    segment['alternatives'], key=lambda x:x["confidence"], reverse=True
                    )[0]['content']

            if segment['type'] == "pronunciation":
                content = f" {content}"

            segment_range += content

        else:
            break #exit from loop

    return segment_range.strip()

