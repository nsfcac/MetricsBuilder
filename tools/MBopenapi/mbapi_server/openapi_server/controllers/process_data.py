import time

def process_node_data(node_list: list, node_data: dict, time_list: list, value: str) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    temp_fields = ["CPU1Temp", "CPU2Temp", "InletTemp"]
    usage_fields = ["CPUUsage", "MemUsage", "NodePower"]
    speed_fields = ["FAN_1", "FAN_2", "FAN_3", "FAN_4"]
    # "jobID"
    time_step = len(time_list)
    for node in node_list:
        json_data[node] = {
            "memory_usage": [],
            "cpu_usage": [],
            "power_usage": [],
            "fan_speed": [],
            "cpu_inl_temp": [],
            "job_id": []
        }

        for i, time in enumerate(time_list):
            # metrics in usage_fields do not need to be aggregated
            for field in usage_fields:
                # rename field names
                if field == "CPUUsage":
                    re_field = "cpu_usage"
                elif field == "MemUsage":
                    re_field = "memory_usage"
                else:
                    re_field = "power_usage"

                field_step = len(node_data[node][field])
                if field_step == 0:
                    json_data[node][re_field].append(None)
                elif field_step != time_step:
                    for item in node_data[node][field]:
                        if item["time"] == time:
                            json_data[node][re_field].append(item[value])
                        else:
                            json_data[node][re_field].append(None)
                else:
                    json_data[node][re_field].append(node_data[node][field][i][value])
            # metrics in temp_fields and speed_fields need to be aggregated, i.e.
            # metrics at the same time stamp are saved in an array
            json_data[node]["cpu_inl_temp"].append([])
            json_data[node]["fan_speed"].append([])
            for field in temp_fields:
                field_step = len(node_data[node][field])
                if field_step == 0:
                    json_data[node]["cpu_inl_temp"][i].append(None)
                elif field_step != time_step:
                    for item in node_data[node][field]:
                        if item["time"] == time:
                            json_data[node]["cpu_inl_temp"][i].append(item[value])
                        else:
                            json_data[node]["cpu_inl_temp"][i].append(None)
                else:
                    json_data[node]["cpu_inl_temp"][i].append(node_data[node][field][i][value])
            for field in speed_fields:
                field_step = len(node_data[node][field])
                if field_step == 0:
                    json_data[node]["fan_speed"][i].append(None)
                elif field_step != time_step:
                    for item in node_data[node][field]:
                        if item["time"] == time:
                            json_data[node]["fan_speed"][i].append(item[value])
                        else:
                            json_data[node]["fan_speed"][i].append(None)
                else:
                    json_data[node]["fan_speed"][i].append(node_data[node][field][i][value])
            
        # process jobID
        json_data[node]["job_id"]= node_data[node]["JobList"]

    return json_data