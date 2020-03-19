import connexion
import six
import time
import json
import datetime

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data
from process_data import  process_node_data


start = 1564660800
end = 1564660800 + 24 * 60 * 60 * 2
interval = "2h"
value = "max"


# Initialization 
config = parse_conf()
node_list = parse_host()
# print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
st = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%SZ')
et = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%SZ')

# print(f"Start time: {st}; End time: {et}")

# Check Sanity

query_start = time.time()
all_data = query_data(node_list, influx, st, et, interval, value)
query_elapsed = float("{0:.2f}".format(time.time() - query_start))
print(f"Query time   : {query_elapsed}")
# print(json.dumps(all_data["job_data"], indent=4))

# process_start = time.time()
# processed_data = process_node_data(node_list, all_data["node_data"], value)
# process_elapsed = float("{0:.2f}".format(time.time() - process_start)) 
# print(f"Porcess time : {process_elapsed}")
# print(json.dumps(processed_data, indent=4))
