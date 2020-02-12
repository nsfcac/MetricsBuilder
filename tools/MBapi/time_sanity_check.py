import time
import datetime
import re

def sanity_check(start: str, end: str, interval: str) -> bool:
    try:
        time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
        st = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        et = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
        if st > et:
            print("Error: Invalid start time and end time!")
            return False
        if not time_valid.match(interval):
            print("Error: Invalid time interval!")
            return False
        return True
    except Exception as err:
        print("Error: " + err.message) 
        return False
        
