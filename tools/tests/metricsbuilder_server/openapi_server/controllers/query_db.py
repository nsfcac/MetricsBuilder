import datetime
import json
import multiprocessing
from openapi_server.controllers.process_data import process_node_data

def query_process_data(node:str, influx: object, start: str, end: str, 
                       interval: str, value: str, time_list: list) -> dict:
    json_data = {}
    try:
        node_data = query_node_data(node, influx, start, end, interval, value)

        # print(f"{node}: ")
        # print(json.dumps(node_data, indent=4))

        if node_data:
            json_data = process_node_data(node, node_data, value, time_list)
    except Exception as err:
        print(err)
        print("Query Data Error!")
    return json_data


def query_node_data(node:str, influx: object, start: str, end: str, 
                    interval: str, value: str) -> dict:
    node_data = {}
    try:
        thermal_labels = ["CPU1Temp", "CPU2Temp", "InletTemp", "FAN_1", "FAN_2", "FAN_3", "FAN_4"]
        uge_labels = ["MemUsage", "CPUUsage"]
        power_labels = ["NodePower"]
        # Get node metrics
        for label in thermal_labels:
            reading = query_reading(influx, node, "Thermal", label, start, end, interval, value)
            node_data[label] = reading
        for label in uge_labels:
            reading = query_reading(influx, node, "UGE", label, start, end, interval, value) 
            node_data[label] = reading
        for label in power_labels:
            reading = query_reading(influx, node, "Power", label, start, end, interval, value)
            node_data[label] = reading
        job_list = query_job_list(influx, node, start, end, interval)

        node_data["JobList"] = job_list

    except Exception as err:
        print(err)
        print("Query Data Error!")
    return node_data


def query_reading(influx: object, node: str, measurement: str, label: str, 
                  start: str, end: str, interval: str, value: str) -> list:
    reading = []
    try:
        query_sql = "SELECT " + value + "(Reading) FROM " + measurement \
                    + " WHERE Label='" + label + "' AND NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY time(" + interval + ") fill(null)"
        reading = influx.get(query_sql)
        
    except Exception as err:
        print(err)
        print("Query Data Error!")
    return reading

def query_job_list(influx: object, node: str, 
                   start: str, end: str, interval: str) -> list:
    job_list = []
    try:
        query_sql = "SELECT DISTINCT(JobList) FROM NodeJobs WHERE NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY *, time(" + interval + ") SLIMIT 1"
        job_list = influx.get(query_sql)
    except Exception as err:
        print(err)
        print("Query Data Error!")
    return job_list

def query_job_data(influx: object, jobid: str) -> dict:
    job_data = {}
    try:
        query_sql = "SELECT * FROM JobsInfo WHERE JobId='" + jobid + "'"
        job_data = influx.get(query_sql)
        if job_data:
            return job_data[0]
    except Exception as err:
        print(err)
        print("Query Data Error!")
    return job_data
