def estimate_finishtime(node_data: dict, time_list: list) -> dict:
    """
    Estimate finish time of jobs by comparing the difference of consecutive NodeJobs
    """
    prev_jobs = []
    jobs_finishtime = {}
    node_jobs = node_data['job_id']
    time_list_len = len(time_list)

    for i, timestamp in enumerate(time_list):
        if i == 0:
            prev_jobs = node_jobs[i]
        else:
            curr_jobs = node_jobs[i]
            for job in prev_jobs:
                if job not in curr_jobs:
                    jobs_finishtime.update({
                        job: timestamp
                    })
            prev_jobs = curr_jobs

    return jobs_finishtime