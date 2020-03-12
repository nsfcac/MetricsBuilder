#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import time

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time, query_data, query_data_job, query_sample_data
from parse_measurements import parse_measurement
from process_data import process_data, process_data_job
from demo import demo

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
    # write_client = QueryInfluxdb(write_config)

    # phase_time = get_phase_time(read_client)

    # start = phase_time[0]
    start = 1555076381
    ten_minute = 10 * 60
    end = start + ten_minute

    st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
    et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))

    
    # Get all system measurements
    print("Analysis measurements...")
    measurements = parse_measurement(read_client)
    sys_measurements = measurements["sys_measurements"]
    job_measurements = measurements["job_measurements"]

    demo(read_client, sys_measurements, job_measurements)

    return


if __name__ == "__main__":
    main()