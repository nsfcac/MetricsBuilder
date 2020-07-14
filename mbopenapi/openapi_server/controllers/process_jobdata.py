def generate_jobset(processed_nodedata: dict) -> set:
    """
    Generate job set from 'job_id'
    """
    flatten = []
    for node, values in processed_nodedata.items():
        job_id = values['job_id']
        flatten = list(set([item for sublist in job_id for item in sublist]))
    return flatten
