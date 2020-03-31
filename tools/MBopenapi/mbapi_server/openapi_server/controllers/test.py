import connexion
import six
import time
import json
import datetime

import multiprocessing
from itertools import repeat

from parse_config import parse_conf, parse_host
from gen_timestamp import gen_timestamp, gen_epoch_timestamp
from DBcm import QueryInfluxdb
from query_db import query_process_data, query_job_data
from gen_timestamp import gen_timestamp


hours = 1
start = 1583020800
end = 1583020800 + hours * 60 * 60
interval = "5m"
value = "max"

all_data = {}
node_data = {}
job_data = {}
# Initialization 
config = parse_conf()
node_list = parse_host()
# node_list = ["10.101.1.1", "10.101.1.2"]
# print(config["influxdb"])
influx = QueryInfluxdb(config["influxdb"])

# Time
st = datetime.datetime.utcfromtimestamp(start)
et = datetime.datetime.utcfromtimestamp(end)

# Time string used in query_data
st_str = st.strftime('%Y-%m-%dT%H:%M:%SZ')
et_str = et.strftime('%Y-%m-%dT%H:%M:%SZ')

cpu_count = multiprocessing.cpu_count()
query_start = time.time()

time_list = gen_timestamp(st, et, interval)

# print(time_list)

# Get all nodes detail
query_process_data_args = zip(node_list, repeat(influx), 
                           repeat(st_str), repeat(et_str), 
                           repeat(interval), repeat(value), repeat(time_list))

with multiprocessing.Pool(processes=cpu_count) as pool:
    results = pool.starmap(query_process_data, query_process_data_args)

all_jobs_list = []

# Attach data to node ip addr
for index, node in enumerate(node_list):
    node_data[node] = results[index]
    try:
        all_jobs_list.extend(results[index]["job_set"])
    except Exception as err:
        print(err)

# print(json.dumps(node_data, indent=4))

# Get all jobs ID
all_jobs_id = list(set(all_jobs_list))

query_job_data_args = zip(repeat(influx), all_jobs_id)

# Get all jobs detail
with multiprocessing.Pool(processes=cpu_count) as pool:
    results = pool.starmap(query_job_data, query_job_data_args)

for index, job in enumerate(all_jobs_id):
    job_data[job] = results[index]

query_elapsed = float("{0:.2f}".format(time.time() - query_start))
print(f"Time for Quering and Processing {hours} of data : {query_elapsed}")

# print(json.dumps(job_data, indent=4))
