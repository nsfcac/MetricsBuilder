import time
from dateutil import parser

from query_db import query_data, query_data_job

def convert_data(read_client: object, write_client: object, 
                 st: str, et: str, measurement: str,
                 error_count: int) -> None:
    """
    Convert data read from read_client and save into write_client
    """
    data = query_data(measurement, read_client, st, et)
    try:
        if data:
            converted_data = process_data(data, measurement, error_count)
            if converted_data:
                write_client.write(converted_data)
    except Exception as err:
        print(err)
    return 

def convert_data_job(read_client: object, write_client: object,
                     measurement: str, error_count: int) -> None:
    """
    Convert job data read from read_client and save into write_client
    """
    data = query_data_job(measurement, read_client)
    try: 
        if data:
            converted_data = process_data_job(data, measurement, error_count)
            if converted_data:
                # write_client.write([converted_data])
                job_id = converted_data["tags"]["JobId"]
                if not check_job(write_client, job_id):
                    write_client.write([converted_data])
    except Exception as err:
        print(err)
    return 

def process_data(data: list, measurement: str, error_count: int) -> list:
    """
    Process data accroding to the schema in measurements
    """
    result = []
    try:
        process_dict = {
            "CPU_Temperature": process_CPU_Temperature,
            "CPU_Usage": process_CPU_Usage,
            "Fan_Speed": process_Fan_Speed,
            "Inlet_Temperature": process_Inlet_Temperature,
            "Job_Info": process_Job_Info,
            "Memory_Usage": process_Memory_Usage,
            "Node_Power_Usage": process_Node_Power_Usage,
            "cluster_unified_metrics": process_cluster_unified_metrics,
            "node_job_info": process_node_job_info,
            "system_metrics": process_system_metrics
        }
        for d in data:
            if process_dict.get(measurement):
                processed_data = process_dict.get(measurement)(d, error_count)
                if processed_data:
                    result.extend(processed_data)
    except Exception as err:
        print(err)
    return result


def process_data_job(data: dict, measurement: str, error_count: int) -> dict:
    """
    Process job info accroding to the schema in measurements
    """
    data_point = None
    try:
        start = int(parser.parse(data["startTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        submit = int(parser.parse(data["submitTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())

        if "i" in measurement:
            nodes = data["nodes"]
            if "," in nodes:
                node_list = nodes.split(",")
            else:
                node_list = [nodes]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": str(measurement.split("i")[1]),
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": str(node_list),
                    "CPUCores": int(data["CPUCores"]), 
                    "JobName": None,
                    "User": data["user"]
                }
            }
            return data_point
        if "j" in measurement:
            nodes = data["nodes"]
            if "," in nodes:
                node_list = nodes.split(",")
            else:
                node_list = [nodes]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": str(measurement.split("-")[1]),
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": str(node_list),
                    "CPUCores": int(data["CPUCores"]), 
                    "JobName": None,
                    "User": data["user"]
                }
            }
            return data_point
        if "qu" in measurement:
            job = measurement
            if "A" in job:
                job_id = job.split("_")[1].replace("A", ".")
            else:
                job_id = job.split("_")[1]

            nodes = data["nodes_address"]
            if "," in nodes:
                node_list = [node.split("-")[0] for node in nodes.split(",")]
            else:
                node_list = [nodes.split("-")[0]]

            data_point = {
                "measurement": "JobsInfo",
                "time": data["time"],
                "tags": {
                    "JobId": str(job_id),
                    "Queue": data["cluster"]
                }, 
                "fields": {
                    "StartTime": start,
                    "SubmitTime": submit,
                    "TotalNodes": len(node_list),
                    "NodeList": str(node_list),
                    "CPUCores": int(data["CPUCores"]), 
                    "JobName": data["app_name"],
                    "User": data["user"]
                }
            }
            return data_point
    except Exception:
        error_count += 1
    return data_point

def process_CPU_Temperature(data: dict, error_count: int) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU1Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU1 Temp"]))
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU2Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU2 Temp"]))
            }
        }
        result = [data_point_1, data_point_2]
    except Exception:
        error_count += 1
    return result


def process_CPU_Usage(data: dict, error_count: int) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host
        
        if data.get("cpuusage") and data["cpuusage"] != 0:
            cpuusage = data["cpuusage"]
        elif data.get("cpuusage(load)") and data["cpuusage(load)"] != 0:
            cpuusage = data["cpuusage(load)"]
        else:
            return result

        data_point = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "CPUUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(cpuusage))
            }
        }
        result = [data_point]
    except Exception:
        error_count += 1
    return result


def process_Fan_Speed(data: dict, error_count: int) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_1",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["FAN_1"]))
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_2",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["FAN_2"]))
            }
        }
        data_point_3 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_3",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["FAN_3"]))
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_4",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["FAN_4"]))
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4]
    except Exception:
        error_count += 1
    return result

def process_Inlet_Temperature(data: dict, error_count: int) -> list: 
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "InletTemp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["Inlet Temp"]))
            }
        }
        result = [data_point]
    except Exception:
        error_count += 1
    return result

# If the data is from Job_Info measurement, 
# the processed data point should be saved to another measurement
def process_Job_Info(data: dict, error_count: int) -> list:
    result = []
    try:
        start = int(parser.parse(data["startTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        submit = int(parser.parse(data["submitTime"], tzinfos={"CDT": "UTC-5", "CST": "UTC-6"}).timestamp())
        
        # Discard the host inforamtion, 
        # since the data stored in this field are not consistent
        # if data["host"][0] == "[":
        #     hostlist = [host[1:-1] for host in data["host"][0:-1].split(", ")]
        # else:
        #     hostlist = [data["host"]]

        data_point = {
            "measurement": "JobsInfo",
            "time": data["time"],
            "tags": {
                "JobId": str(data["jobID"]),
                "Queue": data["cluster"]
            }, 
            "fields": {
                "StartTime": start,
                "SubmitTime": submit,
                "TotalNodes": None,
                "NodeList": None,
                "CPUCores": None,
                "JobName": None,
                "User": data["user"]
            }
        }
        result = [data_point]
    except Exception:
        error_count += 1
    return result


def process_Memory_Usage(data: dict, error_count: int) -> list: 
    result = []
    try:
        available_memory = float(data["available_memory"].split("G")[0])
        total_memory = float(data["total_memory"].split("G")[0])
        mem_usage = (total_memory - available_memory)/total_memory

        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host
         
        data_point = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "MemUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(mem_usage))
            }
        }
        result = [data_point]
    except Exception:
        error_count += 1
    return result


def process_Node_Power_Usage(data: dict, error_count: int) -> list:
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Label": "NodePower",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["powerusage_watts"]))
            }
        }
        result = [data_point]
    except Exception:
        error_count += 1
    return result


def process_cluster_unified_metrics(data: dict, error_count: int) -> list:
    result = []
    try:
        host = data["host"]
        if "compute" in host:
            host_ip = "10.101." + host.split("-")[1] + "." + host.split("-")[2]
        else:
            host_ip = host

        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU1Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU1_temp"]))
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU2Temp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU2_temp"]))
            }
        }
        data_point_3 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "CPUUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(data["cpuusage"]))
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_1",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan1_speed"]))
            }
        }
        data_point_5 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_2",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan2_speed"]))
            }
        }
        data_point_6 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_3",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan3_speed"]))
            }
        }
        data_point_7 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_4",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan4_speed"]))
            }
        }
        data_point_8 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "InletTemp",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["inlet_temp"]))
            }
        }
        data_point_9 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "MemUsage",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(data["memoryusage"]))
            }
        }
        data_point_10 = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Label": "NodePower",
                "NodeId": host_ip
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["powerusage_watts"]))
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4, 
                  data_point_5, data_point_6, data_point_7, data_point_8,
                  data_point_9, data_point_10] 
    except Exception:
        error_count += 1
    return result


def process_node_job_info(data: dict, error_count: int) -> list:
    result = []
    try:
        joblist = [job.split("qu_")[1].replace("A", ".") for job in data["jobID"].split(",")]
        data_point = {
            "measurement": "NodeJobs",
            "time": data["time"],
            "tags": {
                "NodeId": data["host"]
            }, 
            "fields": {
                "JobList": str(joblist)
            }
        }
        result.append(data_point)
    except Exception:
        error_count += 1
    return result


def process_system_metrics(data: dict, error_count: int) -> list:
    result = []
    try:
        joblist = [job.split("qu_")[1].replace("A", ".") for job in data["jobID"].split(",")]
        
        data_point_1 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU1Temp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU1_temp"]))
            }
        }
        data_point_2 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "CPU2Temp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["CPU2_temp"]))
            }
        }
        data_point_3 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "CPUUsage",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(data["cpuusage"]))
            }
        }
        data_point_4 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_1",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan1_speed"]))
            }
        }
        data_point_5 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_2",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan2_speed"]))
            }
        }
        data_point_6 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_3",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan3_speed"]))
            }
        }
        data_point_7 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "FAN_4",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["fan4_speed"]))
            }
        }
        data_point_8 = {
            "measurement": "Thermal",
            "time": data["time"],
            "tags": {
                "Label": "InletTemp",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["inlet_temp"]))
            }
        }
        data_point_9 = {
            "measurement": "UGE",
            "time": data["time"],
            "tags": {
                "Label": "MemUsage",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.4f}".format(data["memoryusage"]))
            }
        }
        data_point_10 = {
            "measurement": "Power",
            "time": data["time"],
            "tags": {
                "Label": "NodePower",
                "NodeId": data["host"]
            }, 
            "fields": {
                "Reading": float("{0:.2f}".format(data["powerusage_watts"]))
            }
        }
        data_point_11 = {
            "measurement": "NodeJobs",
            "time": data["time"],
            "tags": {
                "NodeId": data["host"]
            }, 
            "fields": {
                "JobList": str(joblist)
            }
        }
        result = [data_point_1, data_point_2, data_point_3, data_point_4, 
                  data_point_5, data_point_6, data_point_7, data_point_8,
                  data_point_9, data_point_10, data_point_11] 
    except Exception:
        error_count += 1
    return result


def check_job(client: object, job: str) -> bool:
    try:
        query_str = "SELECT * FROM JobsInfo WHERE JobId = '" + job + "'"
        data = client.get(query_str)
        if data:
            return True
    except Exception as err:
        print(err)

    return False