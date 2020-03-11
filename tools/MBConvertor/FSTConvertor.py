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
    one_day = 24 * 60 * 60
    end = start + one_day

    st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
    et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))

    measurements = parse_measurement(read_client)
    # Get sample data points
    sys_data = []
    for mea in measurements["sys_measurements"]:
        sys_data.append(query_sample_data(read_client, mea))

    job_data = []
    job_data.append(query_sample_data(read_client, measurements["sys_measurements"][0]))
    job_data.append(query_sample_data(read_client, measurements["sys_measurements"][-1]))
    
    with open("sys_data.json", "w") as sysfile:
        json.dump(sys_data, sysfile, indent=2)
    with open("job_data.json", "w") as jobfile:
        json.dump(job_data, jobfile, indent=2)
    
    # print(st)
    # print(et)

    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #             "Memory_Usage", "Fan_Speed", "Node_Power_Usage", "Job_Info"]
    # fst_mea = ["Job_Info"]
    # measurement = "CPU_Temperature"
    # node_list = ["10.101.1.1"]

    # for mea in fst_mea:
    #     json_data = query_data(node_list, mea, read_client, st, et)
    #     if json_data:
    #         updated = process_data(json_data, mea)
    #         print(updated)

    # data_point = query_data_point(read_client)
    # print(json.dumps(data_point, indent=4))

    # Get host list
    # hostlist = parse_host()
    # Get first timestamp
    return


if __name__ == "__main__":
    main()