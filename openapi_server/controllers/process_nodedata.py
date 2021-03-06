import logging


def process_nodedata(nodedata: list, value_type: str, time_list: list) -> list:
    """
    Process node data points read from influxdb
    """
    aggregated = []
    organized = {}

    try:
        for data in nodedata:
            node = data['node']
            measurement = data['measurement']
            label = data['label']
            values = data['values']
            if values:
                if measurement == 'NodeJobs':
                    flatten_values = {}
                    for value in values:
                        timestamp = value["time"]
                        job_str_list = value["distinct"][1:-1].split(', ')
                        job_list = [job[1:-1] for job in job_str_list if job[1:-1]]
                        
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
                    flatten_values = [value[value_type] for value in values]
            else:
                flatten_values = []

            # # Build a dict
            if node in organized:
                if measurement in organized[node]:
                    organized[node][measurement].update({
                        label: flatten_values
                    })
                else:
                    organized[node].update({
                        measurement: {
                            label: flatten_values
                        }
                    })
            else:
                organized.update({
                    node: {
                        measurement: {
                            label: flatten_values
                        }
                    }
                })

        # Aggregate organized data
        for node, metircs in organized.items():
            aggregated.append(aggregate_nodedata(node, metircs, time_list))

    except Exception as err:
        logging.error(f"process_nodedata : process_nodedata : {err}")

    return aggregated


def aggregate_nodedata(node: str, organized: dict, time_list: list) -> dict:
    """
    Aggregate fan speed, temperature
    """
    aggregated = {}
    try:
        # Mapping aggregated data keys to measurements
        mapping = {
            "MemUsage": "memory_usage",
            "CPUUsage": "cpu_usage",
            "Load": "load_short",
            "SwapUsage": "swap_usage",
            "Power": "power_usage",
            "FanSensor": "fan_speed",
            "TempSensor": "cpu_inl_temp",
            "NodeJobs": "job_id"
        }

        # Aggregate and unfold organized data
        for measurement, labels in organized.items():
            new_key = mapping[measurement]
            aggregated.update({
                new_key: []
            })
            labels_list = list(labels.keys())
            if len(labels_list) == 1:
                if new_key == "job_id":
                    label_value = process_joblist(organized[measurement][labels_list[0]], time_list)
                else:
                    label_value = organized[measurement][labels_list[0]]
                aggregated[new_key] = label_value
                # job_set = set([item for sublist in label_value for item in sublist])
                # aggregated["job_set"] = job_set
            else:
                length = len(time_list)
                for i in range(length):
                    all_label_value = []
                    for label in labels_list:
                        try:
                            label_value = organized[measurement][label][i]
                            all_label_value.append(label_value)
                        except:
                            all_label_value.append(None)
                    aggregated[new_key].append(all_label_value)
            
            # # Check length
            # if len(aggregated[new_key]) != len(time_list):
            #         print(f"{node} - {new_key} - {len(label_value)}")
               
    except Exception as err:
        logging.error(f"process_nodedata : aggregate_nodedata : {node} : {err}")

    return {node: aggregated}


def process_joblist(job_list_dict: dict, time_list: list) -> list:
    """
    Interpolate the job list data. 
    For some time stamps, it may not have their corresponding job lists.
    Go through the generated time list, and interpolate the empty slot.
    """
    processed_joblist = []
    # print(job_list_dict)
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