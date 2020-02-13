import re
from datetime import datetime, timedelta

def time_delta(timeInterval: str) -> str:
    """Validate time interval and generate timedelta object"""
    time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
    if not time_valid.match(timeInterval):
        return None
    if "s" in timeInterval:
        num = int(timeInterval.split('s')[0])
        delta = timedelta(seconds = num)
    elif "m" in timeInterval:
        num = int(timeInterval.split('m')[0])
        delta = timedelta(minutes = num)
    elif "h" in timeInterval:
        num = int(timeInterval.split('h')[0])
        delta = timedelta(hours = num)
    elif "d" in timeInterval:
        num = int(timeInterval.split('d')[0])
        delta = timedelta(days = num)
    else:
        num = int(timeInterval.split('w')[0])
        delta = timedelta(weeks = num)
    return delta

def datetime_range(start: str, end: str, interval: str) -> str:
    """Generate time interval array"""
    current = start
    while current < end:
        yield current
        current += interval

def time_stamp(start: str, end: str, interval: str) -> list:
    st = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
    ed = datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
    delta = time_delta(interval)
    time_list = [dt.strftime("%Y-%m-%dT%H:%M:%SZ") for dt in datetime_range(
        st, ed, delta
    )]
    return time_list