import datetime
import json

def query_data(node_list: list, influx: object, start: str, end: str, interval: str, value: str) -> dict:
    json_data = {}
    node_data = {}
    job_data = {}
    all_job_list = []
    all_job = []

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
            
            all_jobs = []
            for item in job_list:
                all_jobs.extend([i[1:-1] for i in item["distinct"][1:-1].split(", ")])
            job_set = list(set(all_jobs))
            print(job_set)
            
            # job_list = [job[1:-1].split(", ") for job in job_list_str]
        #     node_data[node]["JobList"] = job_list

        #     for jobs in job_list:
        #         all_job_list.extend(jobs)

        # all_job = list(set(all_job_list))
        # for job in all_job:
        #     job_data[job] = query_job_data(influx, job)

        # Get jobs metrics
        json_data.update({
            "node_data": node_data,
            "job_data": job_data
        })
    except Exception as err:
        print(err)
    return json_data


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
    return reading

def query_job_list(influx: object, node: str, 
                   start: str, end: str, interval: str) -> list:
    job_list = []
    try:
        query_sql = "SELECT DISTINCT(JobList) FROM NodeJobs WHERE NodeId='" + node \
                    + "' AND time >= '" + start + "' AND time < '" + end \
                    + "' GROUP BY time(" + interval + ") fill(previous)"
        print(query_sql)
        job_list = influx.get(query_sql)
    except Exception as err:
        print(err)
    return job_list

def query_job_data(influx: object, jobid: str) -> dict:
    job_data = {}
    try:
        query_sql = "SELECT * FROM JobsInfo WHERE JobId='" + jobid + "'"
        job_data = influx.get(query_sql)[0]
    except Exception as err:
        print(err)
    return job_data
