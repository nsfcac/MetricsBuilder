import time

def process_all_data(node_list: list, all_data: dict, value: str) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    # try:
    for node in node_list:
        memory_usage = [item[value] for item in all_data["node_data"][node]["MemUsage"]]
        cpu_usage = [item[value] for item in all_data["node_data"][node]["CPUUsage"]]
        power_usage = [item[value] for item in all_data["node_data"][node]["NodePower"]]
        
        CPU1Temp = [item[value] for item in all_data["node_data"][node]["CPU1Temp"]]
        CPU2Temp = [item[value] for item in all_data["node_data"][node]["CPU2Temp"]]
        InletTemp = [item[value] for item in all_data["node_data"][node]["InletTemp"]]

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

        FAN_1 = [item[value] for item in all_data["node_data"][node]["FAN_1"]]
        FAN_2 = [item[value] for item in all_data["node_data"][node]["FAN_2"]]
        FAN_3 = [item[value] for item in all_data["node_data"][node]["FAN_3"]]
        FAN_4 = [item[value] for item in all_data["node_data"][node]["FAN_4"]]

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

        json_data[node] = {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "cpu_inl_temp": cpu_inl_temp,
            "job_id": all_data["job_data"]
        }
    # except Exception as err:
    #     print(err)
    return json_data