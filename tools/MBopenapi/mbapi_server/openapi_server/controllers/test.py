import connexion
import six
import time
import json
import datetime
import multiprocessing as mp

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_data, query_node_data
from process_data import process_node_data


hours = 24 * 2
start = 1564228800
end = 1564228800 + hours * 60 * 60
interval = "5m"
value = "max"


# Initialization 
config = parse_conf()
node_list = parse_host()
# node_list = ["10.101.1.1", "10.101.1.2"]
# print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time string used in query_data
st = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%SZ')
et = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%SZ')

# print(f"Start time: {st}; End time: {et}")

# out_queue = mp.Queue()

query_start = time.time()

# workers = [mp.Process(target=query_node_data, args=(node, influx, st , et, interval, value, out_queue)) for node in node_list]

# for worker in workers:
#     worker.start()
# for worker in workers:
#     worker.join()

# all_data = {}
# for index, host in enumerate(node_list):
#     all_data[host] = out_queue.get()

# print(json.dumps(all_data, indent=4))

all_data = query_data(node_list, influx, st, et, interval, value)

query_elapsed = float("{0:.2f}".format(time.time() - query_start))
print(f"Time for Quering {hours} of data : {query_elapsed}")
# print(json.dumps(all_data["job_data"], indent=4))

# process_start = time.time()
# processed_data = process_node_data(node_list, all_data["node_data"], value)
# process_elapsed = float("{0:.2f}".format(time.time() - process_start)) 
# print(f"Porcess time : {process_elapsed}")
# print(json.dumps(processed_data, indent=4))
