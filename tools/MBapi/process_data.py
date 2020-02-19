def process_node_data(node_list: list, node_data: dict, time_list: list, value: str) -> dict:
    json_data = {}
    temp_fields = ["CPU1_temp", "CPU2_temp", "inlet_temp"]
    usage_fields = ["cpuusage", "memoryusage", "powerusage_watts"]
    speed_fields = ["fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed"]
    # "jobID"
    for node in node_list:
        json_data[node] = {}
        # temperature fields are saved in the same array
        for field in temp_fields:
            json_data[node][field] = []
            if field == "jobID":
                jobid_tmp = []
                for item in node_data[node][field]:
                    job_obj = {}
                    job_obj["time"] = item["time"]
                    job_obj["distinct"] = id_de_duplicate(item["distinct"])
                    jobid_tmp.append(job_obj)
                # print(jobid_tmp)
                json_data[node][field] = agg_time_job(jobid_tmp, time_list)
            else:
                json_data[node][field] = check_field(node_data[node][field], time_list)
                
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

    
