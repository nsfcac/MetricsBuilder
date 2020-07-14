def process_nodedata(nodedata: list) -> dict:

    organized = {}

    for data in nodedata:
        # Get node, measurement, label names
        node = data['node']
        measurement = data["data"]["name"]
        label = data['label']
        values = data["data"]["values"]

        if measurement == "NodeJobs":
            for value in values:
                flatten_values = {
                    value[0]: value[1][1:-1].split(",")
                }
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

    job_list = organized["NodeJobs"]["JobList"]

    json_data = {
        "memory_usage": memory_usage,
        "cpu_usage": cpu_usage,
        "power_usage": power_usage,
        "fan_speed": fan_speed,
        "cpu_inl_temp": cpu_inl_temp,
        "job_list": job_list,
    }

    return json_data