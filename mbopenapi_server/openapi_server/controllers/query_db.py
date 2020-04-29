import datetime
import json
import logging
import multiprocessing

# For testing
# from process_data import process_node_data
from openapi_server.controllers.process_data import process_node_data

def query_process_data(node:str, client: object, start: str, end: str, 
                       interval: str, value: str, time_list: list) -> dict:
    json_data = {}
    try:
        node_data = query_node_data(node, client, start, end, interval, value)

        # print(f"{node}: ")
        # print(json.dumps(node_data, indent=4))

        if node_data:
            json_data = process_node_data(node, node_data, value, time_list)
    except:
        logging.error(f"Failed to query and process data of node: {node}, time range: {start} - {end}, interval: {interval}, value: {value}")
    return json_data


def query_node_data(node:str, client: object, start: str, end: str, 
                    interval: str, value: str) -> dict:
    node_data = {}
    try:
        thermal_labels = ["CPU1Temp", "CPU2Temp", "InletTemp", "FAN_1", "FAN_2", "FAN_3", "FAN_4"]
        uge_labels = ["MemUsage", "CPUUsage"]
        power_labels = ["NodePower"]
        # Get node metrics
        for label in thermal_labels:
            reading = query_reading(client, node, "Thermal", label, start, end, interval, value)
            node_data[label] = reading
        for label in uge_labels:
            reading = query_reading(client, node, "UGE", label, start, end, interval, value) 
            node_data[label] = reading
        for label in power_labels:
            reading = query_reading(client, node, "Power", label, start, end, interval, value)
            node_data[label] = reading
        
        job_list = query_job_list(client, node, start, end, interval)

        node_data["JobList"] = job_list

    except:
        logging.error(f"Failed to query data of node: {node}, time range: {start} - {end}, interval: {interval}, value: {value}")
    return node_data


def query_reading(client: object, node: str, measurement: str, label: str, 
                  start: str, end: str, interval: str, value: str) -> list:
    reading = []
    try:
        query_sql = "SELECT " + value + "(Reading) FROM " + measurement \
                    + " WHERE Label='" + label + "' AND NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY time(" + interval + ") fill(null)"
        reading = list( client.query(query_sql).get_points() )
        
    except:
        logging.error(f"Failed to query {measurement} of node: {node}, time range: {start} - {end}, interval: {interval}, value: {value}")
    return reading

def query_job_list(client: object, node: str, 
                   start: str, end: str, interval: str) -> list:
    # SELECT DISTINCT(JobList) FROM NodeJobs WHERE NodeId='10.101.1.1' AND time >= '2020-04-06T12:00:00Z' AND time < '2020-04-07T12:00:00Z' GROUP BY *, time(2h) SLIMIT 1
    job_list = []
    try:
        query_sql = "SELECT DISTINCT(JobList) FROM NodeJobs WHERE NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY *, time(" + interval + ") SLIMIT 1"
        job_list = list( client.query(query_sql).get_points() )
    except:
        logging.error(f"Failed to query job list of node: {node}")
    return job_list

def query_job_data(client: object, jobid: str) -> dict:
    job_data = {}
    try:
        query_sql = "SELECT * FROM JobsInfo WHERE JobId='" + jobid + "'"
        job_data = list( client.query(query_sql).get_points() )
        if job_data:
            return job_data[0]
    except:
        logging.error(f"Failed to query data of job: {jobid}")
    return job_data
