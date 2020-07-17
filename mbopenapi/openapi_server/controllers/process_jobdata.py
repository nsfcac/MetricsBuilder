import logging


def process_jobdata(jobdata: list) -> dict:
    """
    Process job data based on the mapping relationship
    """
    processed_jobdata = {}
    try:
        for data in jobdata:
            job = data["job"]
            job_array = False
            mapping = {
                "StartTime": "start_time",
                "SubmitTime": "submit_time",
                "JobName": "job_name",
                "User": "user_name",
                "NodeList": "node_list",
                "TotalNodes": "total_nodes",
                "CPUCores": "cpu_cores"
            }

            values = data["values"][0]

            processed_jobdata.update({
                job: {
                    "finish_time": None
                }
            })
            
            for key, value in values.items():
                if key != "time" and key != "JobId":
                    processed_jobdata[job].update({
                        mapping[key]: value
                    })

            # Convert node list (as string) to node list (as array)
            node_list_str = processed_jobdata[job]["node_list"]
            node_list_str_arr = node_list_str[1:-1].split(", ")
            node_list_arr = [item[1:-1] for item in node_list_str_arr]

            processed_jobdata[job].update({
                "node_list": node_list_arr
            })


    except Exception as err:
        logging.error(f"process_jobdata : {job} : {err}")
    
    return processed_jobdata