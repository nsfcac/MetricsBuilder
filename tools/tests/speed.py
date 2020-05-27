import requests
import time
from datetime import datetime
import zlib, json, base64

# Ref: https://medium.com/@busybus/zipjson-3ed15f8ea85d

ZIPJSON_KEY = 'base64(zip(o))'

def json_unzip(j, insist=True):
    try:
        assert (j[ZIPJSON_KEY])
        assert (set(j.keys()) == {ZIPJSON_KEY})
    except:
        if insist:
            raise RuntimeError("JSON not in the expected format {" + str(ZIPJSON_KEY) + ": zipstring}")
        else:
            return j

    try:
        j = zlib.decompress(base64.b64decode(j[ZIPJSON_KEY]))
    except:
        raise RuntimeError("Could not decode/unzip the contents")

    try:
        j = json.loads(j)
    except:
        raise RuntimeError("Could interpret the unzipped contents")

    return j

start_str = "2020-02-14T12:00:00Z"
end_str = "2020-02-14T18:00:00Z"
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

response_json = json.loads(response.content)

print("time_stamp")
print(json_unzip(response_json["time_stamp"]))

print("jobs_info")
print(json_unzip(response_json["jobs_info"]))

print("nodes_info")
print(json_unzip(response_json["nodes_info"]))

# Time Range in seconds
time_range = int(end.timestamp()) - int(start.timestamp())

# with open("requests.log", "a+") as requests_log:
#     print(f"{data_size} MB|{time_range}|{interval}|{value}|{total_elapsed}", file = requests_log)