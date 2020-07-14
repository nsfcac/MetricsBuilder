import logging


def process_nodedata(nodedata: list, time_list: list) -> dict:
    """
    Process node data points read from influxdb
    """
    aggregated = {}
    organized = {}
    try:
        for data in nodedata:
            node = data['node']
            measurement = data['measurement']
            label = data['label']
            values = data['values']

            # If returned valid values, process
            if values:
                if measurement == 'NodeJobs':
                    flatten_values = {}
                    for value in values:
                        timestamp = value[0]
                        job_str_list = value[1][1:-1].split(', ')
                        job_list = [job[1:-1] for job in job_str_list]
                        
                        # For Job list data, it's possible that several returned data
                        # points have the same time stamp when using DISTINCT in sql.
                        # Aggregate the data with the same time stamp here
                        if timestamp in flatten_values:
                            flatten_values[timestamp].extend(job_list)
                        else:
                            flatten_values.update({
                                timestamp: job_list
                            })
                else:
                    # Aggregate data points
                    flatten_values = [value[1] for value in values]
            else:
                flatten_values = []

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

            # Aggregate organized data
            aggregated = aggregate_nodedata(node, organized, time_list)

    except Exception as err:
        logging.error(f"process_nodedata : process_nodedata : {err}")

    return aggregated


def aggregate_nodedata(node: str, organized: dict, time_list: list) -> dict:
    """
    Aggregate fan speed, temperature
    """
    nodedata = {}
    aggregated = {}
    try:
        # Mapping aggregated data keys to measurements
        mapping = {
            "MemUsage": "memory_usage",
            "CPUUsage": "cpu_usage",
            "Power": "power_usage",
            "FanSensor": "fan_speed",
            "TempSensor": "cpu_inl_temp",
            "NodeJobs": "job_list"
        }

        # Aggregate and unfold organized data
        for measurement, labels in organized.items():
            new_key = mapping[measurement]
            aggregated.update({
                new_key: []
            })
            labels_list = list(labels.keys())
            if len(labels_list) == 1:
                aggregated[new_key] = organized[measurement][labels_list[0]]
            else:
                length = len(organized[measurement][labels_list[0]])
                for i in range(length):
                    all_label_value = []
                    for label in labels_list:
                        label_value = organized[measurement][label][i]
                        all_label_value.append(label_value)
                    aggregated[new_key].append(all_label_value)

        # # Process Job list
        # joblist = aggregated["NodeJobs"]
        # processed_joblist = process_joblist(joblist, time_list)
        # aggregated.update({
        #     "NodeJobs": processed_joblist
        # })

        # nodedata = {
        #     node: {
        #         "memory_usage": memory_usage,
        #         "cpu_usage": cpu_usage,
        #         "power_usage": power_usage,
        #         "fan_speed": fan_speed,
        #         "cpu_inl_temp": cpu_inl_temp,
        #         "job_list": job_list
        #     }
        # }

    except Exception as err:
        logging.error(f"process_nodedata : aggregate_nodedata : {node} : {err}")

    return aggregated


def process_joblist(job_list_dict: dict, time_list: list) -> list:
    """
    Interpolate the job list data. 
    For some time stamps, it may not have their corresponding job lists.
    Go through the generated time list, and interpolate the empty slot.
    """
    processed_joblist = []
    try:
        for i, t in enumerate(time_list):
            if i == 0:
                this_job_list = job_list_dict.get(t, [])
            else:
                this_job_list = job_list_dict.get(t, processed_joblist[i-1])
            processed_joblist.append(this_job_list)
    except Exception as err:
        logging.error(f"process_nodedata : process_joblist : {err}")
    return processed_joblist