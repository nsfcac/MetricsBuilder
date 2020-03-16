#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import json
import time

import multiprocessing
from itertools import repeat

from DBcm import QueryInfluxdb
from parse_config import parse_host
from query_db import get_phase_time, query_data, query_data_job, query_sample_data
from parse_measurements import parse_measurement
from process_data import process_data, process_data_job, convert_data, convert_data_job
from demo import demo

read_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'hpcc_monitoring_db'
}

write_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'test_schema' # updated_schema
}

def main():

    # Initialization
    read_client = QueryInfluxdb(read_config)
    write_client = QueryInfluxdb(write_config)

    # Get cpu counts
    cpu_count = multiprocessing.cpu_count()
    error_count = 0
    # phase_time = get_phase_time(read_client)

    first =  1552539600
    # last = 1583301600
    last = 1552712400
    step = 1 * 60 * 60
    
    # Get all system measurements
    print("Analysis measurements...")
    measurements = parse_measurement(read_client)
    sys_measurements = measurements["sys_measurements"]
    job_measurements = measurements["job_measurements"]

    # # Converting job metrics in parallel
    # convert_data_job_args = zip(repeat(read_client), repeat(write_client), 
    #                         job_measurements, repeat(error_count))
    # with multiprocessing.Pool(processes=cpu_count) as pool:
    #     pool.starmap(convert_data_job, convert_data_job_args)

    # Converting system metrics in parallel
    for start in range(first, last, step):
        end = start + step

        st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
        et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))
    
        convert_data_args = zip(repeat(read_client), repeat(write_client), 
                            repeat(st), repeat(et), sys_measurements,
                            repeat(error_count))
        with multiprocessing.Pool(processes=cpu_count) as pool:
            pool.starmap(convert_data, convert_data_args)
        print(start)

    # For demo
    # demo(read_client, sys_measurements, job_measurements)

    return


if __name__ == "__main__":
    main()