#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import time
import datetime

import multiprocessing
from itertools import repeat

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time, query_data, query_data_job, query_sample_data
from parse_measurements import parse_measurement
from process_data import process_data, process_data_job, convert_data, convert_data_job
# from demo import demo

read_config = {
    'host': '10.10.1.4',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

write_config = {
    'host': 'localhost',
    'port': '8086',
    # 'database': 'test_schema'
    'database': 'updated_schema'
}

def main():

    # Initialization
    read_client = QueryInfluxdb(read_config)
    write_client = QueryInfluxdb(write_config)

    # Get cpu counts
    cpu_count = multiprocessing.cpu_count()
    error_count = 0
    # phase_time = get_phase_time(read_client)

    # # Phase 1: Thursday, March 14, 2019 12:00:00 AM GMT-05:00 - Friday, April 10, 2020 12:00:00 PM GMT-05:00
    # first = 1552539600
    # last = 1586520000

    # Phase 2: Friday, April 10, 2020 12:00:00 PM GMT-05:00 - Friday, April 24, 2020 12:00:00 PM GMT-05:00
    # first = 1586520000
    # last = 1587729600

    # Phase 3: Friday, April 24, 2020 12:00:00 PM GMT-05:00 - Tuesday, April 28, 2020 11:40:00 AM GMT-05:00
    first = 1587729600
    last = 1588092000
    step = 3600
    
    # Get all system measurements

    # print("Analysis measurements...")
    measurements = parse_measurement(read_client)
    sys_measurements = measurements["sys_measurements"]
    job_measurements = measurements["job_measurements"]

    # Converting job metrics in parallel
    convert_data_job_args = zip(repeat(read_client), repeat(write_client), 
                            job_measurements, repeat(error_count))
    with multiprocessing.Pool(processes=cpu_count) as pool:
        pool.starmap(convert_data_job, convert_data_job_args)

    # Converting system metrics in parallel
    for start in range(first, last, step):
        end = start + step

        st = datetime.datetime.utcfromtimestamp(start).strftime('%Y-%m-%dT%H:%M:%SZ')
        et = datetime.datetime.utcfromtimestamp(end).strftime('%Y-%m-%dT%H:%M:%SZ')
    
        convert_data_args = zip(repeat(read_client), repeat(write_client), 
                            repeat(st), repeat(et), sys_measurements,
                            repeat(error_count))
        with multiprocessing.Pool(processes=cpu_count) as pool:
            pool.starmap(convert_data, convert_data_args)

    # For demo
    # demo(read_client, sys_measurements, job_measurements)
    print(error_count)
    return


if __name__ == "__main__":
    main()