def node_data_parser(node_list: list, node_data: dict) -> dict:
    json_data = {}
    fields = ["CPU1_temp", "CPU2_temp", "CPUCores", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts", "jobID"]
    for node in node_list:
        json_data[node] = {}
        for field in fields:
            json_data[node][field] = []
            if field == "jobID":
                for item in node_data[node][field]:
                    job_arr = id_de_duplicate(item["distinct"])
                    json_data[node][field].append(job_arr)
            else:
                for item in node_data[node][field]:
                    json_data[node][field].append(item['max'])
        
    print(json_data[node])
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

def job_data_parser(job_info: dict) -> dict:
    json_data = {}
    job_arr = []

    for key, value in job_info.items():
        if "A" in key:
            qu_job_id = key.split("A")[0]
            job_id = qu_job_id.split("_")[1]
        else:
            job_id = qu_job_id.split("_")[1]

        if job_id not in job_arr:
            json_data[job_id] = value
            job_arr.append(job_id)

    return json_data

    
