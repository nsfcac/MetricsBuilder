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

            values = data["values"]["values"][0]

            processed_jobdata.update({
                job: {
                    "finish_time": None
                }
            })
            
            for i, value in enumerate(values):
                if value != "time" and value != "JobId":
                    processed_jobdata[job].update({
                        mapping[value]: values[i]
                    })


    except Exception as err:
        logging.error(f"process_jobdata : {job} : {err}")
    
    return processed_jobdata