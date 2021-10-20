import re
from datetime import datetime, timedelta
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'


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
    start = datetime.strptime(start, DATETIME_FORMAT)
    end = datetime.strptime(end, DATETIME_FORMAT)
    current = start
    while current <= end:
        yield current
        current += interval


def gen_timelist(start: str, end: str, interval: str) -> list:
    delta = time_delta(interval)
    time_list = [dt.strftime("%Y-%m-%dT%H:%M:%SZ") for dt in datetime_range(
        start, end, delta
    )]
    return time_list


def gen_epoch_timelist(start: str, end: str, interval: str) -> list:
    delta = time_delta(interval)
    time_list = [int(dt.timestamp()) for dt in datetime_range(
        start, end, delta
    )]
    return time_list


# start = '2021-06-28T13:00:00'
# end = '2021-06-28T14:00:00'
# interval = '5 min'

# time_list = gen_epoch_timelist(start, end, interval)

# print(time_list)
# print(len(time_list))