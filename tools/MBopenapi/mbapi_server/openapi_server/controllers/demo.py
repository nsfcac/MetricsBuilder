import connexion
import six
import time
import json

from parse_config import parse_conf
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data

start = "2020-02-12T00:00:00Z"
end = "2020-02-12T00:10:00Z"
interval = "5m"
value = "max"


# Initialization 
config = parse_conf()
node_list = ['10.101.1.1']
print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
start_str = start
end_str = end

print(f"Start time str: {start_str}; End time str: {end_str}")

# Check Sanity
if start > end:
    print("Start time should no larger than end time")
else:

    query_start = time.time()

    all_data = query_data(node_list, influx, start_str, end_str, interval, value)

    query_elapsed = float("{0:.2f}".format(time.time() - query_start))

    print(query_elapsed)
    print(json.dumps(all_data, indent=4))
