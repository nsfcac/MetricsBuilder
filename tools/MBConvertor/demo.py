import json
import time

from query_db import get_phase_time, query_data, query_data_job, query_sample_data
from process_data import process_data, process_data_job


def demo(read_client: object, sys_measurements: list, job_measurements: list) -> None:
    """
    Convertor demo, it only process 10 minutes of data
    """
    start = 1555076381
    ten_minute = 10 * 60
    end = start + ten_minute

    st = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(start))
    et = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(end))
    
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

    print("-------------------------------------------------------")
    print(f"All measurements       :{len(job_measurements) + len(sys_measurements)}")
    print(f"Numerical measurements :{len(process_dict)}")
    print(f"Jobs measurements      :{len(job_measurements)}")
    print(f"Other measurements     :{len(sys_measurements) - len(process_dict)}")
    print("-------------------------------------------------------")

    for mea in sys_measurements:
        if mea in process_dict:
            json_data = query_data(mea, read_client, st, et)
            if json_data:
                print(f"Converting {mea}...")
                print("---- Original data point ----")
                print(json.dumps(json_data[-10], indent=4))

                converted_data_point = process_data(json_data[-10], mea)
                print("---- Converted data point ----")
                print(json.dumps(converted_data_point, indent=4))
                print("-------------------------------------------------------")
            # data_points.append(converted_data_point)
    # print(json.dumps(data_points, indent=4))

    # Convert job metrics
    job_measurements = ["i764687", "j-775882", "qu_1082110A434"]
    # data_points = []
    for mea in job_measurements:
        print(f"Converting {mea}...")
        json_data = query_data_job(mea, read_client)
        if json_data:
            print("---- Original data point ----")
            print(json.dumps(json_data, indent=4))

            converted_data_point = process_data_job(json_data, mea)
            print("---- Converted data point ----")
            print(json.dumps(converted_data_point, indent=4))
            print("-------------------------------------------------------")
    return