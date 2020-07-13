def process_nodedata(nodedata: list) -> dict:

    processed_data = {}

    for data in nodedata:
        # Get node - measurement - label names
        node = data['node']
        measurement = data["data"]["name"]
        label = data['label']
        values = data["data"]["values"]

        # Aggregate data points
        flatten_values = [value[1] for value in values]

        # Build a dict
        if measurement in processed_data:
            processed_data[measurement].update({
                label: flatten_values
            })
        else:
            processed_data.update({
                measurement: {
                    label: flatten_values
                }
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

    return processed_data