import time
import json
import multiprocessing

def process_node_data(node: str, node_data: dict, value: str) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    try:
        memory_usage = [item[value] for item in node_data["MemUsage"]]
        cpu_usage = [item[value] for item in node_data["CPUUsage"]]
        power_usage = [item[value] for item in node_data["NodePower"]]
        
        CPU1Temp = [item[value] for item in node_data["CPU1Temp"]]
        CPU2Temp = [item[value] for item in node_data["CPU2Temp"]]
        InletTemp = [item[value] for item in node_data["InletTemp"]]

        cpu_inl_temp = []
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

        FAN_1 = [item[value] for item in node_data["FAN_1"]]
        FAN_2 = [item[value] for item in node_data["FAN_2"]]
        FAN_3 = [item[value] for item in node_data["FAN_3"]]
        FAN_4 = [item[value] for item in node_data["FAN_4"]]

        fan_speed = []
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

        job_list_dict = {}
        all_jobs_list = []

        for item in node_data["JobList"]:
            if item["distinct"]:
                job_list_dict[item["time"]] = [jobstr[1:-1] for jobstr in item["distinct"][1:-1].split(", ")]
                all_jobs_list.append(job_list_dict[item["time"]])
            else:
                job_list_dict[item["time"]] = []
        
        all_jobs = list(set(all_jobs_list))

        print(json.dumps(all_jobs, indent=4))

        json_data = {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "cpu_inl_temp": cpu_inl_temp,
            "job_id": job_list_dict,
            "all_jobs": all_jobs
        }

    except Exception as err:
        print(err)
    return json_data