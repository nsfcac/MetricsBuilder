import requests
from datetime import datetime
import time

start_str = "2020-02-14T12:00:00"
end_str = "2020-02-14T18:00:00"
interval = "5m"
value = "max"

query_str = "\http://129.118.104.141:8080/v1/metrics?start=" + start_str + "&end=" + end_str + "&interval=" + interval + "&value=" + value

start = datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%SZ')
end = datetime.strptime(end_str, '%Y-%m-%dT%H:%M:%SZ')

query_start = time.time()

response = requests.get(query_str)

data_size = len(response.encode("utf-8"))

total_elapsed = float("{0:.2f}".format(time.time() - query_start))
# In seconds
time_range = int(end.timestamp()) - int(start.timestamp())

with open("requests.log", "a+") as requests_log:
    print(f"{data_size}B|{time_range}|{interval}|{value}|{total_elapsed}", file = requests_log)