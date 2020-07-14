import logging


def process_nodedata(nodedata: list, measurements: dict, time_list: list) -> dict:
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
            aggregated = aggregate_nodedata(node, organized, measurements, time_list)

    except Exception as err:
        logging.error(f"process_nodedata : process_nodedata : {err}")

    return aggregated


def aggregate_nodedata(node: str, organized: dict, 
                       measurements: dict, time_list: list) -> dict:
    """
    Aggregate fan speed, temperature
    """
    aggregated = {}
    try:
        # Mapping aggregated data keys to measurements
        mapping = {
            "memory_usage" : "MemUsage",
            "cpu_usage": "CPUUsage",
            "power_usage": "Power",
            "fan_speed": "FanSensor",
            "cpu_inl_temp": "TempSensor",
            "job_list": "NodeJobs"
        }

        mapping_keys = list(mapping.keys())

        for measurement, labels in measurements.items():
            aggregated.update({
                measurement: []
            })
            if len(labels) == 1:
                aggregated[measurement] = organized[measurement][labels[0]]
            else:
                length = len(organized[measurement][labels[0]])
                for i in range(length):
                    all_label_value = []
                    for label in labels:
                        label_value = organized[measurement][label][i]
                        all_label_value.append(label_value)
                    aggregated[measurement].append(all_label_value)


        # aggregated = {
        #     node: {
        #         "memory_usage": memory_usage,
        #         "cpu_usage": cpu_usage,
        #         "power_usage": power_usage,
        #         "fan_speed": fan_speed,
        #         "cpu_inl_temp": cpu_inl_temp,
        #         "job_list": job_list
        #     }
        # }

        # print(f"Memory usage : {len(memory_usage)}")
        # print(f"CPU usage : {len(cpu_usage)}")
        # print(f"Power usage : {len(power_usage)}")
        # print(f"Fan speed : {len(fan_speed)}")
        # print(f"Temperature : {len(cpu_inl_temp)}")
        # print(f"Job list : {len(job_list)}")

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