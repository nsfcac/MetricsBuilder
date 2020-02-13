def node_data_parser(node_list: list, node_data: dict) -> dict:
    json_data = {}
    fields = ["CPU1_temp", "CPU2_temp", "CPUCores", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts", "jobID"]
    for node in node_list:
        json_data[node] = {}
        for field in fields:
            json_data[node][field] = []
            if field == "jobID":
                raw_job_list = node_data[node][field][0]['distinct']
                job_list = []
                for item in raw_job_list:
                    if "A" in item:
                        qu_job_id = item.split('A')[0]
                        job_id = qu_job_id.split('_')[1]
                        if job_id not in job_list:
                            job_list.append(job_id)
                    else:
                        job_list.append(item.split('_')[1])
