import datetime
import json
import multiprocessing


def query_data(node_list: list, influx: object, start: str, end: str, interval: str, value: str) -> dict:
    json_data = {}
    node_data = {}
    job_data = {}
    all_job_list = []

    try:
        thermal_labels = ["CPU1Temp", "CPU2Temp", "InletTemp", "FAN_1", "FAN_2", "FAN_3", "FAN_4"]
        uge_labels = ["MemUsage", "CPUUsage"]
        power_labels = ["NodePower"]

        # Get nodes metrics
        for node in node_list:
            node_data[node] = {}
            for label in thermal_labels:
                reading = query_reading(influx, node, "Thermal", label, start, end, interval, value)
                node_data[node][label] = reading
            for label in uge_labels:
                reading = query_reading(influx, node, "UGE", label, start, end, interval, value) 
                node_data[node][label] = reading
            for label in power_labels:
                reading = query_reading(influx, node, "Power", label, start, end, interval, value)
                node_data[node][label] = reading
            job_list = query_job_list(influx, node, start, end, interval)

            node_data[node]["JobList"] = job_list
            
            # print(json.dumps(job_list, indent=4))

            for item in job_list:
                all_job_list.extend([i[1:-1] for i in item["distinct"][1:-1].split(", ")])
        
        # Get jobs metrics
        job_set = list(set(all_job_list))
        
        for job in job_set:
            job_data[job] = query_job_data(influx, job)
        
        json_data.update({
            "node_data": node_data,
            "job_data": job_data
        })
        # print(json.dumps(json_data, indent=4))
    except Exception as err:
        print(err)
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
    return node_data


def query_reading(influx: object, node: str, measurement: str, label: str, 
                  start: str, end: str, interval: str, value: str) -> list:
    reading = []
    try:
        query_sql = "SELECT " + value + "(Reading) FROM " + measurement \
                    + " WHERE Label='" + label + "' AND NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY time(" + interval + ") fill(null)"
        # print(query_sql)
        reading = influx.get(query_sql)
        
    except Exception as err:
        print(err)
    return reading

def query_job_list(influx: object, node: str, 
                   start: str, end: str, interval: str) -> list:
    job_list = []
    try:
        query_sql = "SELECT DISTINCT(JobList) FROM NodeJobs WHERE NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY time(" + interval + ") fill(previous)"
        job_list = influx.get(query_sql)
    except Exception as err:
        print(err)
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
    return job_data
