import json
import multiprocessing
from itertools import repeat
import sys
sys.path.append('../')

import util
from mb_utils import parse_nodelist
from controllers.query_nodedata import query_nodedata
from controllers.process_nodedata import process_nodedata
from controllers.generate_timelist import gen_timelist, gen_epoch_timelist

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

query_nodedata_args = zip(node_list, repeat(influx_cfg), repeat(measurements),
                          repeat(start), repeat(end), repeat(interval), repeat(value))

with multiprocessing.Pool() as pool:
    # query data
    results = pool.starmap(query_nodedata, query_nodedata_args)
    # process data
    process_nodedata_args = zip(results, repeat(time_list))
    processed_results = pool.starmap(process_nodedata, process_nodedata_args)

# node = '10.101.2.35'
# nodedata = query_nodedata(node, influx_cfg, measurements, start, end, interval, value)

# results = process_nodedata(nodedata, time_list)
print(json.dumps(processed_results, indent=4))
# print(json.dumps(results, indent=4))