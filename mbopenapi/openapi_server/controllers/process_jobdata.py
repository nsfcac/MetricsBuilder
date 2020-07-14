import logging


def generate_jobset(processed_nodedata: dict) -> set:
    """
    Generate job set from 'job_id'
    """
    flatten = []
    try:
        for node, values in processed_nodedata.items():
            job_id = values['job_id']
            flatten = list(set([item for sublist in job_id for item in sublist]))
    except Exception as err:
        logging.error(f"generate_jobset : {err}")
    return flatten


def process_jobdata(jobdata: dict) -> dict:
    """
    Process job data based on the mapping relationship
    """
    job = jobdata["job"]
    processed_jobdata = {}
    job_array = False
    try:
        mapping = {
            "StartTime": "start_time",
            "SubmitTime": "submit_time",
            "JobName": "job_name",
            "User": "user_name",
            "NodeList": "node_list",
            "TotalNodes": "total_nodes",
            "CPUCores": "cpu_cores"
        }

        columns = jobdata["values"]["columns"]
        values = jobdata["values"]["values"][0]

        for i, column in enumerate(columns):
            if column != "time" and column != "JobId":
                processed_jobdata.update({
                    mapping[column]: values[i]
                })
            else:
                processed_jobdata.update({
                    "finish_time": None
                })
    except Exception as err:
        logging.error(f"process_jobdata : {job} : {err}")
    
    return {job: processed_jobdata}