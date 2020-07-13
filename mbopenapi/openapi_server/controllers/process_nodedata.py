def process_nodedata(nodedata: list) -> dict:

    processed = {}

    for data in nodedata:
        node = data['node']
        label = data['label']
        values = data["data"]["values"]
        flatten_values = [value[1] for value in values]

        processed.update({
            label: flatten_values
        })

    # json_data = {
    #         "memory_usage": memory_usage,
    #         "cpu_usage": cpu_usage,
    #         "power_usage": power_usage,
    #         "fan_speed": fan_speed,
    #         "cpu_inl_temp": cpu_inl_temp,
    #         "job_list": job_list,
    #         "job_set": job_set
    #     }

    return processed