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
    print("Analysis measurements...")
    measurements = parse_measurement(read_client)
    sys_measurements = measurements["sys_measurements"]
    job_measurements = measurements["job_measurements"]

    print(f"System measurements: {len(sys_measurements)}")
    print(f"Jobs measurements: {len(job_measurements)}")

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
    #     "measurement": job_measurements[0],
    #     "details": query_sample_data(read_client, job_measurements[0])
    # }
    # job_data.append(data_obj)

    # for job in job_measurements:
    #     if "j" in job:
    #         data_obj = {
    #             "measurement": job,
    #             "details": query_sample_data(read_client, job_measurements[0])
    #         }
    #         job_data.append(data_obj)
    #         break

    # data_obj = {
    #     "measurement": job_measurements[-1],
    #     "details": query_sample_data(read_client, job_measurements[-1])
    # }
    # job_data.append(data_obj)
    
    # with open("sys_data.json", "w") as sysfile:
    #     json.dump(sys_data, sysfile, indent=2)
    # with open("job_data.json", "w") as jobfile:
    #     json.dump(job_data, jobfile, indent=2)
    # --------------------------------------------------------------------------
    
    # print(sys_measurements)

    # Convert system metrics
    # data_points = []

    process_dict = [
        "CPU_Temperature",
        "CPU_Usage",
        "Fan_Speed",
        "Inlet_Temperature",
        "Job_Info",
        "Memory_Usage",
        "Node_Power_Usage",
        "cluster_unified_metrics",
        "node_job_info",
        "system_metrics"
    ]

    for mea in sys_measurements:
        if mea in process_dict:
            json_data = query_data(mea, read_client, st, et)
            if json_data:
                print(f"Converting {mea}...")
                print(f"Original data point:")
                print(json.dumps(json_data[0], indent=4))

                converted_data_point = process_data(json_data[0], mea)
                print(f"Converted data point:")
                print(json.dumps(converted_data_point, indent=4))

            # data_points.append(converted_data_point)
    # print(json.dumps(data_points, indent=4))

    # Convert job metrics
    job_measurements = ["i764687", "j-775882", "qu_1082110A434"]
    # data_points = []
    for mea in job_measurements:
        print(f"Converting {mea}...")
        json_data = query_data_job(mea, read_client)
        if json_data:
            print(f"Original data point:")
            print(json.dumps(json_data, indent=4))

            converted_data_point = process_data_job(json_data, mea)
            print(f"Converted data point:")
            print(json.dumps(converted_data_point, indent=4))

            # data_points.append(process_data_job(json_data, mea))

    # Convert job metrics
    # print(job_measurements[-1])
    # job_data = query_data_job(job_measurements[-1], read_client)
    # print(job_data)

    # data_point = query_data_point(read_client)
    # print(json.dumps(data_point, indent=4))

    # Get host list
    # hostlist = parse_host()
    # Get first timestamp
    return


if __name__ == "__main__":
    main()