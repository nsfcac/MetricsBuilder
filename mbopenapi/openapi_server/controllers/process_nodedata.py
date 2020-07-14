import logging


def process_nodedata(nodedata: list, time_list: list) -> dict:

    organized = {}

    for data in nodedata:
        # If node data is None, do no process
        if data["data"]:
            # Get node, measurement, label names
            node = data['node']
            measurement = data["data"]["name"]
            label = data['label']
            values = data["data"]["values"]

            if measurement == "NodeJobs":
                flatten_values = {}
                for value in values:
                    timestamp = value[0]
                    job_str_list = value[1][1:-1].split(", ")
                    job_list = [job[1:-1] for job in job_str_list]
                    # For Job list data, it's possible that several returned data
                    # points have the same time stamp when using DISTINCT in sql.
                    # Aggregate the data with the same time stamp here
                    if value[0] in flatten_values:
                        flatten_values[timestamp].extend(job_list)
                    else:
                        flatten_values.update({
                            timestamp: job_list
                        })
            else:
                # Aggregate data points
                flatten_values = [value[1] for value in values]

            # Build a dict
            if measurement in organized:
                organized[measurement].update({
                    label: flatten_values
                })
            else:
                organized.update({
                    measurement: {
                        label: flatten_values
                    }
                })
    """
    # Mapping data points
    # To do: make it automatically
    memory_usage = organized["MemUsage"]["UGE"]
    cpu_usage = organized["CPUUsage"]["UGE"]
    power_usage = organized["Power"]["NodePower"]

    fan_1 = organized["FanSensor"]["FAN_1"]
    fan_2 = organized["FanSensor"]["FAN_2"]
    fan_3 = organized["FanSensor"]["FAN_3"]
    fan_4 = organized["FanSensor"]["FAN_4"]

    fan_speed = [ [fan_1[i], fan_2[i], fan_3[i], fan_4[i]] for i in range(len(fan_1)) ]

    cpu_1_temp = organized["TempSensor"]["CPU1 Temp"]
    cpu_2_temp = organized["TempSensor"]["CPU2 Temp"]
    inlet_temp = organized["TempSensor"]["Inlet Temp"]

    cpu_inl_temp = [ [cpu_1_temp[i], cpu_2_temp[i], inlet_temp[i]] for i in range(len(cpu_1_temp)) ]

    job_list_dict = organized["NodeJobs"]["JobList"]
    job_list = process_joblist(job_list_dict, time_list)

    json_data = {
        "memory_usage": memory_usage,
        "cpu_usage": cpu_usage,
        "power_usage": power_usage,
        "fan_speed": fan_speed,
        "cpu_inl_temp": cpu_inl_temp,
        "job_list": job_list,
    }
    """
    return organized


def process_joblist(joblist: dict, time_list: list) -> list:
    """
    Interpolate the job list data. 
    For some time stamps, it may not have their corresponding job lists.
    Go through the generated time list, and interpolate the empty slot.
    """
    processed_joblist = []
    try:
        for i, t in enumerate(time_list):
            if i == 0:
                this_job_list = joblist.get(t, [])
            else:
                this_job_list = joblist.get(t, joblist[i-1])
            processed_joblist.append(this_job_list)
    except Exception as err:
        logging.error(f"process_nodedata : process_joblist error : {err}")
    return processed_joblist