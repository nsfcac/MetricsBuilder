import time
import json
import multiprocessing

def process_node_data(node: str, node_data: dict, value: str, time_list: list) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    memory_usage = []
    cpu_usage = []
    power_usage = []
    cpu_inl_temp = []
    fan_speed = []
    job_list_dict = {}
    job_list_temp = []
    job_list = []
    job_set = []
    db_time_list = []
    try:
        if node_data["MemUsage"]:
            memory_usage = [item[value] for item in node_data["MemUsage"]]

        if node_data["CPUUsage"]:
            cpu_usage = [item[value] for item in node_data["CPUUsage"]]
                
        if node_data["NodePower"]:
            power_usage = [item[value] for item in node_data["NodePower"]]
        
        if node_data["CPU1Temp"] and node_data["CPU2Temp"] and node_data["InletTemp"]:
            CPU1Temp = [item[value] for item in node_data["CPU1Temp"]]
            CPU2Temp = [item[value] for item in node_data["CPU2Temp"]]
            InletTemp = [item[value] for item in node_data["InletTemp"]]

            for index, item in enumerate(CPU1Temp):
                cpu_inl_temp.append([])
                if item:
                    cpu_inl_temp[index].append(item)
                else:
                    cpu_inl_temp[index].append(None)
                if CPU2Temp[index]:
                    cpu_inl_temp[index].append(CPU2Temp[index])
                else:
                    cpu_inl_temp[index].append(None)
                if InletTemp[index]:
                    cpu_inl_temp[index].append(InletTemp[index])
                else:
                    cpu_inl_temp[index].append(None)

        if node_data["FAN_1"] and node_data["FAN_2"] and node_data["FAN_3"] and node_data["FAN_4"]:
            FAN_1 = [item[value] for item in node_data["FAN_1"]]
            FAN_2 = [item[value] for item in node_data["FAN_2"]]
            FAN_3 = [item[value] for item in node_data["FAN_3"]]
            FAN_4 = [item[value] for item in node_data["FAN_4"]]

            for index, item in enumerate(FAN_1):
                fan_speed.append([])
                if item:
                    fan_speed[index].append(item)
                else:
                    fan_speed[index].append(None)
                if FAN_2[index]:
                    fan_speed[index].append(FAN_2[index])
                else:
                    fan_speed[index].append(None)
                if FAN_3[index]:
                    fan_speed[index].append(FAN_3[index])
                else:
                    fan_speed[index].append(None)
                if FAN_4[index]:
                    fan_speed[index].append(FAN_4[index])
                else:
                    fan_speed[index].append(None)

        if node_data["JobList"]:
            for item in node_data["JobList"]:
                # Aggregate the value with the same time
                this_job_list = [jobstr[1:-1] for jobstr in item["distinct"][1:-1].split(", ")]
                if item["time"] not in db_time_list:
                    db_time_list.append(item["time"])
                    job_list_dict[item["time"]] = this_job_list
                else:
                    job_list_dict[item["time"]].extend(this_job_list)

        print("job_list_dict")
        print(json.dumps(job_list_dict, indent=4))
        
        # Interpolate
        for i, t in enumerate(time_list):
            if i == 0:
                if t not in job_list_dict:
                    this_job_list = []
                else:
                    this_job_list = job_list_dict[t]
            else:
                if t in job_list_dict:
                    this_job_list = job_list_dict[t]
                else:
                    this_job_list = job_list[i-1]
            job_list.append(this_job_list)

        print("job_list")
        print(json.dumps(job_list, indent=4))
        
        
        job_set = list(set(job_list_temp))
        
        json_data = {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "cpu_inl_temp": cpu_inl_temp,
            "job_list": job_list,
            "job_set": job_set
        }

        # print(f"memory_usage length : {len(memory_usage)}")
        # print(f"cpu_usage length    : {len(cpu_usage)}")
        # print(f"power_usage length  : {len(power_usage)}")
        # print(f"fan_speed length    : {len(fan_speed)}")
        # print(f"cpu_inl_temp length : {len(cpu_inl_temp)}")
        # print(f"job_list length     : {len(job_list)}")

    except Exception as err:
        print(err)
        print("Process Data Error!")
    return json_data