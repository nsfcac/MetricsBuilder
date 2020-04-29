import re
import time
import datetime
import requests

from flask import Flask
from flask import request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/')
def router() -> str:

    args = request.args

    if "starttime" in args and "endtime" in args and "interval" in args:
        startTime = request.args["starttime"]
        endTime = request.args["endtime"]
        interval = request.args["interval"]

        if time_sanity_check(startTime, endTime, interval):
            url = "http://10.10.1.4:5000/api/v1/?starttime=" + startTime + "&endtime=" + endTime + "&interval=" + interval
            result = requests.get(url)
        else:
            result = "Error: Invalid start time, end time and/or interval!"

    else:
        result = "Warning: Please specify start time, end time and interval!"
    
    return result


def time_sanity_check(start: str, end: str, interval: str) -> bool:
    try:
        time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
        st = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        et = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
        if st > et:
            # print("Error: Invalid start time and end time!")
            return False
        if not time_valid.match(interval):
            # print("Error: Invalid time interval!")
            return False
        return True
    except Exception:
        # print(err) 
        return False


if __name__ == '__main__':
    app.run(host='0.0.0.0')