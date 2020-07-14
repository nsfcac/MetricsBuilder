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
    processed_jobdata = {}
    job = jobdata["job"]
    columns = jobdata["values"]["columns"]
    values = jobdata["values"]["values"][0]

    for i, column in enumerate(columns):
        jobdata.update({
            column: values[i]
        })
    
    return {job: processed_jobdata}