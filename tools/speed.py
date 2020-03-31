import requests
from datetime import datetime
import time

start_str = "2020-02-14T12:00:00Z"
end_str = "2020-02-17T12:00:00Z"
interval = "5m"
value = "max"

query_str = "http://129.118.104.141:8080/v1/metrics?start=" + start_str + "&end=" + end_str + "&interval=" + interval + "&value=" + value

start = datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%SZ')
end = datetime.strptime(end_str, '%Y-%m-%dT%H:%M:%SZ')

query_start = time.time()

response = requests.get(query_str)


total_elapsed = float("{0:.2f}".format(time.time() - query_start))

# Data Size in MB
data_size = float("{0:.2f}".format(len(response.content)/(1024*1024)))

# Time Range in seconds
time_range = int(end.timestamp()) - int(start.timestamp())

with open("requests.log", "a+") as requests_log:
    print(f"{data_size} MB|{time_range}|{interval}|{value}|{total_elapsed}", file = requests_log)