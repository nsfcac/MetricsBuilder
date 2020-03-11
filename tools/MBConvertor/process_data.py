import time

def process_data(json_data: list, measurement: str) -> list:
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #         "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    result = []
    try:
        for data in json_data:
            if measurement == "CPU_Temperature":
                data_point_1 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "CPU1Temp",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["CPU1 Temp"]
                    }
                }
                data_point_2 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "CPU2Temp",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["CPU2 Temp"]
                    }
                }
                result.append(data_point_1)
                result.append(data_point_2)
                continue
            if measurement == "Inlet_Temperature":
                data_point = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "InletTemp",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["Inlet Temp"]
                    }
                }
                result.append(data_point)
                continue
            if measurement == "CPU_Usage":
                data_point = {
                    "measurement" : "UGE",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "CPUUsage",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": float("{0:.2f}".format(data["cpuusage(load)"]))
                    }
                }
                result.append(data_point)
                continue
            if measurement == "Memory_Usage":
                available_memory = float(data["available_memory"].split("G")[0])
                total_memory = float(data["total_memory"].split("G")[0])
                mem_usage = (total_memory - available_memory)/total_memory
                
                data_point = {
                    "measurement" : "UGE",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "MemUsage",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": float("{0:.2f}".format(mem_usage))
                    }
                }

                result.append(data_point)
                continue
            if measurement == "Fan_Speed":
                data_point_1 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "FAN_1",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["FAN_1"]
                    }
                }
                data_point_2 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "FAN_2",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["FAN_2"]
                    }
                }
                data_point_3 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "FAN_3",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["FAN_3"]
                    }
                }
                data_point_4 = {
                    "measurement" : "Thermal",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "FAN_4",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["FAN_4"]
                    }
                }
                result.append(data_point_1)
                result.append(data_point_2)
                result.append(data_point_3)
                result.append(data_point_4)
                continue
            if measurement == "Node_Power_Usage":
                data_point = {
                    "measurement" : "Power",
                    "time": data["time"],
                    "tags": {
                        "Sensor": "NodePower",
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "Reading": data["powerusage_watts"]
                    }
                }
                result.append(data_point)
                continue
            if measurement == "Job_Info":
                data_point_1 = {
                    "measurement" : "NodeJobs",
                    "time": data["time"],
                    "tags": {
                        "NodeId": data["host"]
                    }, 
                    "fields": {
                        "JobList": data["jobID"]
                    }
                }
                result.append(data_point_1)

                job_list = []
                if data["jobID"] not in job_list:
                    job_list.append(data["jobID"])

                    time_pattern = "%a %b %d %X %Z %Y"
                    start = int(time.mktime(time.strptime(data["startTime"], time_pattern)))
                    submit = int(time.mktime(time.strptime(data["submitTime"], time_pattern)))

                    data_point_2 = {
                        "measurement" : "JobsInfo",
                        "time": data["time"],
                        "tags": {
                            "JobId": data["jobID"],
                            "Queue": data["cluster"]
                        }, 
                        "fields": {
                            "StartTime": start,
                            "SubmitTime": submit,
                            "NodeList": None,
                            "CPUCores": None,
                            "JobName": None,
                            "User": data["user"],
                        }
                    }
                    result.append(data_point_2)
                
    except Exception as err:
        print(err)
    
    return result

