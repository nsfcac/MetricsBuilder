import json
import multiprocessing
from itertools import repeat
import asyncio
import sys
sys.path.append('../')

import util
from mb_utils import parse_nodelist
from controllers.query_nodedata import query_nodedata
# from controllers.query_jobdata import query_jobdata
from controllers.process_nodedata import process_nodedata
from controllers.generate_timelist import gen_timelist, gen_epoch_timelist
# from controllers.process_jobdata import generate_jobset, process_jobdata

influx_cfg = {
    "host": "10.10.1.3",
    "port": "8086",
    "database": "hpcc_metrics_phase2",
  }

nodelist_cfg = [
    "10.101.1/1-60",
    "10.101.2/1-60",
    "10.101.3/1-56",
    "10.101.4/1-48",
    "10.101.5/1-24",
    "10.101.6/1-20",
    "10.101.7/1-3,5-60",
    "10.101.8/1-60",
    "10.101.9/1-60",
    "10.101.10/25-44"
]

measurements = {
    "Power": [
        "NodePower"
    ],
    "FanSensor": [
        "FAN_1",
        "FAN_2",
        "FAN_3",
        "FAN_4"
    ],
    "TempSensor": [
        "CPU1 Temp",
        "CPU2 Temp",
        "Inlet Temp"
    ],
    "CPUUsage": [
        "UGE"
    ],
    "MemUsage": [
        "UGE"
    ],
    "NodeJobs": [
        "JobList"
  ]
}

node_list = parse_nodelist(nodelist_cfg)

start = "2020-07-12T12:00:00-05:00"
end = "2020-07-12T18:00:00-05:00"
interval = "5m"
value = "max"

start_time = util.deserialize_datetime(start)
end_time = util.deserialize_datetime(end)

time_list = gen_epoch_timelist(start_time, end_time, interval)
# print(json.dumps(time_list, indent = 4))

# # cores= multiprocessing.cpu_count()

# node_list = ["10.101.1.1", "10.101.2.35", "10.101.1.3"]
# node_list = ['10.101.2.35']


# query_nodedata_args = zip(node_list, repeat(influx_cfg), repeat(measurements),
#                           repeat(start), repeat(end), repeat(interval), repeat(value), repeat(loop))

# with multiprocessing.Pool() as pool:
#     # query data
#     results = pool.starmap(query_nodedata, query_nodedata_args)
    # # process data
    # process_nodedata_args = zip(results, repeat(time_list))
    # processd_nodedata = pool.starmap(process_nodedata, process_nodedata_args)
    # all_jobset = pool.map(generate_jobset, processd_nodedata)

nodedata = query_nodedata(node_list, influx_cfg, measurements, start, end, interval, value, time_list)

node_data = {}

for node_group in nodedata:
    for node in node_group:
        for key, value in node.items():
            node_data.update({
                key: value
            })


# node_data = {}

# for data in processd_nodedata:
#     for key, value in data.items():
#         node_data.update({
#             key: value
#         })

# flatten_jobset = list(set([item for sublist in all_jobset for item in sublist]))
# all_jobdata = query_jobdata(flatten_jobset, influx_cfg)

# with multiprocessing.Pool() as pool:
#     processed_jobdata = pool.map(process_jobdata, all_jobdata)

# job_data = {}
# for data in processed_jobdata:
#     for key, value in data.items():
#         job_data.update({
#             key: value
#         })
        
print(json.dumps(node_data, indent=4))