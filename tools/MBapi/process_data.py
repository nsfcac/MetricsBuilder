def process_node_data(node_list: list, node_data: dict, time_list: list, value: str) -> dict:
    """
    Process node data retrieved from influxdb
    """
    json_data = {}
    temp_fields = ["CPU1_temp", "CPU2_temp", "inlet_temp"]
    usage_fields = ["cpuusage", "memoryusage", "powerusage_watts"]
    speed_fields = ["fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed"]
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
                if field == "cpuusage":
                    re_field = "cpu_usage"
                elif field == "memoryusage":
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
            json_data[node]["job_id"].append([])
            for item in node_data[node]["jobID"]:
                if item["time"] == time:
                    tmp = set(json_data[node]["job_id"][i] + item["distinct"])
                    json_data[node]["job_id"][i] = list(tmp)
    return json_data

# Process array job id and de-duplicate 
def id_de_duplicate(job_list: list) -> list:
    jobs = []
    for item in job_list:
        if "A" in item:
            qu_job_id = item.split("A")[0]
            job_id = qu_job_id.split("_")[1]
        else:
            job_id = item.split("_")[1]
        if job_id not in jobs:
                jobs.append(job_id)
    return jobs

# DISTINCT may have duplicated value at one timestamp
def agg_time_job(job_id_arr: list, time_list: list) -> list:
    time_arr = []
    updated_job_obj = []
    tmp_obj = {}
    result = []

    for item in job_id_arr:
        if item["time"] not in time_arr:
            updated_job_obj.append(item)
            time_arr.append(item["time"])
        else:
            for i in updated_job_obj:
                if i["time"] == item["time"]:
                    all_jobs = i["distinct"] + item["distinct"]
                    i["distinct"] = list(set(all_jobs))
    
    for item in updated_job_obj:
        tmp_obj[item["time"]] = item["distinct"]

    for time in time_list:
        if time in tmp_obj:
            result.append(tmp_obj[time])
        else:
            result.append([])
    # print(result)
    return result

# Add None value
def check_field(field: list, time_list: list) -> list:
    tmp_obj = {}
    result = []

    for item in field:
        tmp_obj[item["time"]] = item["max"]

    for time in time_list:
        if time in tmp_obj:
            result.append(tmp_obj[time])
        else:
            result.append(None)

    return result


def job_data_parser(job_info: dict) -> dict:
    json_data = {}
    job_arr = []

    for key, value in job_info.items():
        if "A" in key:
            qu_job_id = key.split("A")[0]
            job_id = qu_job_id.split("_")[1]
        else:
            job_id = key.split("_")[1]

        if job_id not in job_arr:
            json_data[job_id] = value
            job_arr.append(job_id)

    return json_data

    
