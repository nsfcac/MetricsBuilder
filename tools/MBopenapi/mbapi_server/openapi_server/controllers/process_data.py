import time

def process_node_data(node_list: list, node_data: dict, value: str) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    # try:
    for node in node_list:
        memory_usage = [item[value] for item in node_data[node]["MemUsage"]]
        cpu_usage = [item[value] for item in node_data[node]["CPUUsage"]]
        power_usage = [item[value] for item in node_data[node]["NodePower"]]
        
        CPU1Temp = [item[value] for item in node_data[node]["CPU1Temp"]]
        CPU2Temp = [item[value] for item in node_data[node]["CPU2Temp"]]
        InletTemp = [item[value] for item in node_data[node]["InletTemp"]]

        cpu_inl_temp = []
        for index, item in enumerate(CPU1Temp):
            cpu_inl_temp.append([])
            cpu_inl_temp[index].append(item)
            cpu_inl_temp[index].extend(CPU2Temp[index])
            cpu_inl_temp[index].extend(InletTemp[index])

        FAN_1 = [item[value] for item in node_data[node]["FAN_1"]]
        FAN_2 = [item[value] for item in node_data[node]["FAN_2"]]
        FAN_3 = [item[value] for item in node_data[node]["FAN_3"]]
        FAN_4 = [item[value] for item in node_data[node]["FAN_4"]]

        fan_speed = []
        for index, item in enumerate(FAN_1):
            fan_speed.append([])
            fan_speed[index].append(item)
            fan_speed[index].append(FAN_2[index])
            fan_speed[index].append(FAN_3[index])
            fan_speed[index].append(FAN_4[index])
    
        json_data[node] = {
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage,
            "power_usage": power_usage,
            "fan_speed": fan_speed,
            "cpu_inl_temp": cpu_inl_temp,
            "job_id": node_data[node]["JobList"]
        }
    # except Exception as err:
    #     print(err)
    return json_data