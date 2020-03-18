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
from demo import demo

read_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'updated_schema'
}

write_config = {
    'host': 'localhost',
    'port': '8086',
    'database': 'test_schema' #  hpcc_monitoring
}

def main():

    # Initialization
    read_client = QueryInfluxdb(read_config)
    write_client = QueryInfluxdb(write_config)

    # Get cpu counts
    cpu_count = multiprocessing.cpu_count()
    # phase_time = get_phase_time(read_client)

    first =  1552539600
    last = 1552543200
    # last = 1583301600
    step = 1 * 60 * 60
    
    datetime.datetime.utcfromtimestamp(1566479392).strftime('%Y-%m-%dT%H:%M:%SZ')
    # Get all system measurements
    # print("Analysis measurements...")
    sys_measurements = ["Thermal", "UGE", "Power", "NodeJobs"]
    job_measurements = ["JobsInfo"]

    # Converting job metrics in parallel
    for start in range(first, last, step):
        end = start + step
        convert_data_job_args = zip(repeat(read_client), repeat(write_client), 
                                repeat(start), repeat(end),job_measurements)
        with multiprocessing.Pool(processes=cpu_count) as pool:
            pool.starmap(convert_data_job, convert_data_job_args)

    # # Converting system metrics in parallel
    # for start in range(first, last, step):
    #     end = start + step

    #     st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
    #     et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))
    
    #     convert_data_args = zip(repeat(read_client), repeat(write_client), 
    #                         repeat(st), repeat(et), sys_measurements)
    #     with multiprocessing.Pool(processes=cpu_count) as pool:
    #         pool.starmap(convert_data, convert_data_args)
    return


def convert_data_job(read_client: object, write_client: object, 
                     start: int, end: int, job_measurement: str):
    # Query job info
    try:
        result = []
        data_job_sql = "SELECT * FROM JobsInfo WHERE time >= " + str(start) + " AND time < " + str(end)
        print(data_job_sql)
        data_job = read_client.get(data_job_sql)
        for job in data_job:
            data_point = {
                "measurement": "JobsInfo",
                "time": datetime.datetime.utcfromtimestamp(job["time"]).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "tags": {
                    "JobId": job["JobId"],
                    "Queue": job["Queue"]
                }, 
                "fields": {
                    "StartTime": job["StartTime"],
                    "SubmitTime": job["SubmitTime"],
                    "TotalNodes": job["TotalNodes"],
                    "NodeList": job["NodeList"],
                    "CPUCores": job["CPUCores"], 
                    "JobName": job["JobName"],
                    "User": job["User"]
                }
            }
            result.extend(data_point)
        if result:
            write_client.write(result)
    except Exception as err:
        print(err)
    return

if __name__ == "__main__":
    main()