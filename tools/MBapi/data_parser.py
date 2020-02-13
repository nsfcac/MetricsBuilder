def node_data_parser(node_list: list, node_data: dict) -> dict:
    json_data = {}
    fields = ["CPU1_temp", "CPU2_temp", "CPUCores", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts"]
    for node in node_list:
        json_data[node] = {}
        for field in fields:
            json_data[node][field] = []
            if field == "jobID":
                jobid_tmp = []
                for item in node_data[node][field]:
                    job_obj = {}
                    job_obj["time"] = item["time"]
                    job_obj["distinct"] = id_de_duplicate(item["distinct"])
                    jobid_tmp.append(job_obj)
                print(jobid_tmp)
                json_data[node][field] = agg_time_job(jobid_tmp)
            else:
                for item in node_data[node][field]:
                    json_data[node][field].append(item['max'])
        
    return json_data


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


def agg_time_job(job_id_arr: list) -> list:
    time_arr = []
    updated_job_obj = []
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
    
    print(updated_job_obj)
    for item in updated_job_obj:
        result.append(item["distinct"])
    print(result)
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

    
