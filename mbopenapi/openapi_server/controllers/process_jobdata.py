def generate_jobset(processed_nodedata: dict) -> set:
    """
    Generate job set from 'job_id'
    """
    flatten = []
    for node, values in processed_nodedata.items():
        job_id = values['job_id']
        flatten = list(set([item for sublist in job_id for item in sublist]))
    return flatten


def process_jobdata(jobdata: dict) -> dict:
    """
    Process job data based on the mapping relationship
    """
    processed_jobdata = {}
    organized_jobdata = {}

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

    organized_jobdata = {}
    job = jobdata["job"]
    columns = jobdata["values"]["columns"]
    values = jobdata["values"]["values"][0]

    for i, column in enumerate(columns):
        if column != "time" and column != "JobId":
            organized_jobdata.update({
                mapping[column]: values[i]
            })
        else:
            organized_jobdata.update({
                "finish_time": None
            })
    
    return {job: organized_jobdata}