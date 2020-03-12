#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import time

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time, query_data, query_sample_data
from parse_measurements import parse_measurement
from process_data import process_data

read_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

write_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'updated_schema'
}

def main():

    # Initialization
    read_client = QueryInfluxdb(read_config)
    write_client = QueryInfluxdb(write_config)

    phase_time = get_phase_time(read_client)
    # print(phase_time)

    # start = phase_time[0]
    start = 1555076381
    ten_minute = 10 * 60
    end = start + ten_minute
    # one_day = 24 * 60 * 60
    # end = start + one_day

    st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
    et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))

    
    # Get all system measurements
    measurements = parse_measurement(read_client)
    sys_measurements = measurements["sys_measurements"]

    # Get sample data points----------------------------------------------------
    # sys_data = []
    # for mea in measurements["sys_measurements"]:
    #     data_obj = {
    #         "measurement": mea,
    #         "details": query_sample_data(read_client, mea)
    #     }
    #     sys_data.append(data_obj)

    # job_data = []
    # data_obj = {
    #     "measurement": measurements["job_measurements"][0],
    #     "details": query_sample_data(read_client, measurements["job_measurements"][0])
    # }
    # job_data.append(data_obj)
    # data_obj = {
    #     "measurement": measurements["job_measurements"][-1],
    #     "details": query_sample_data(read_client, measurements["job_measurements"][-1])
    # }
    # job_data.append(data_obj)
    
    # with open("sys_data.json", "w") as sysfile:
    #     json.dump(sys_data, sysfile, indent=2)
    # with open("job_data.json", "w") as jobfile:
    #     json.dump(job_data, jobfile, indent=2)
    # --------------------------------------------------------------------------
    
    # print(st)
    # print(et)
    data_points = []
    for mea in sys_measurements:
        json_data = query_data(mea, read_client, st, et)
        if json_data:
            data_points.extend(process_data(json_data, mea))

    print(data_points)
    
    # data_point = query_data_point(read_client)
    # print(json.dumps(data_point, indent=4))

    # Get host list
    # hostlist = parse_host()
    # Get first timestamp
    return


if __name__ == "__main__":
    main()