import connexion
import six
import time
import json

from parse_config import parse_conf
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data

start = 1581469200000000
end = 1581472800000000
interval = "5m"
value = "max"


# Initialization 
config = parse_conf()
node_list = ['10.101.1.1']
print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
start_epoch = start
end_epoch = end

print(f"Start time: {start_epoch}; End time: {end_epoch}")

# Check Sanity

all_data = query_data(node_list, influx, start_epoch, end_epoch, interval, value)

print(json.dumps(all_data, indent=4))
