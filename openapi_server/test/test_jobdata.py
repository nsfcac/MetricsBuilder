import json
import multiprocessing
from itertools import repeat
from influxdb import InfluxDBClient

import sys
sys.path.append('../')

import util
from mb_utils import parse_nodelist
from controllers.query_nodedata import query_nodedata
from controllers.query_jobdata import query_jobdata
from controllers.process_nodedata import process_nodedata
from controllers.generate_timelist import gen_timelist, gen_epoch_timelist
from controllers.estimate_finishtime import estimate_finishtime

influx_cfg = {
    "host": "10.10.1.3",
    "port": "8086",
    "database": "hpcc_metrics_phase2",
  }

nodelist_cfg = [
    "10.101.1.[1-60]",
    "10.101.2.[1-60]",
    "10.101.3.[1-56]",
    "10.101.4.[1-48]",
    "10.101.5.[1-24]",
    "10.101.6.[1-20]",
    "10.101.7.[1-3,5-60]",
    "10.101.8.[1-60]",
    "10.101.9.[1-60]",
    "10.101.10.[25-44]"
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
end = "2020-07-12T14:00:00-05:00"
interval = "5m"
value_type = "max"

start_time = util.deserialize_datetime(start)
end_time = util.deserialize_datetime(end)

offset = f"{int(start_time.timestamp())}s"

start_time_epoch = int(start_time.timestamp()) * 1000000000
end_time_epoch = int(end_time.timestamp()) * 1000000000

time_list = gen_epoch_timelist(start_time, end_time, interval)

client = InfluxDBClient(host=influx_cfg['host'], port=influx_cfg['port'], database=influx_cfg['database'])

processed_nodedata = query_nodedata(node_list, client, measurements, str(start_time_epoch), str(end_time_epoch), offset, interval, value_type, time_list)

node_data = {}

for node_group in processed_nodedata:
    for node in node_group:
        for key, value in node.items():
            node_data.update({
                key: value
            })

node_data_list = list(node_data.values())


with multiprocessing.Pool() as pool:
    estimate_finishtime_args = zip(node_data_list, repeat(time_list))
    jobs_finishtime_temp = pool.starmap(estimate_finishtime, estimate_finishtime_args)

jobs_finishtime = {}

for jobs in jobs_finishtime_temp:
    if jobs:
        for job_id, finishtime in jobs.items():
            jobs_finishtime.update({
                job_id: finishtime
            })


# processed_jobdata = query_jobdata(processed_nodedata, client)

# job_data = {}
# for job_group in processed_jobdata:
#     for key, value in job_group.items():
#         job_data.update({
#             key: value
#         })


print(json.dumps(jobs_finishtime, indent=4))