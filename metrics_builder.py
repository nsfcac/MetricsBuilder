import json

def main():
    job_set = get_job_set("jobs.json")
    exec_hosts = get_exec_hosts("exechosts.json")
    job_node_match = match_job_node(job_set, exec_hosts)

    print(job_node_match)
    print('Job node matches length:'),
    print(len(job_node_match))
    # print("Job Set: "),
    # print(job_set)

# Get job set
def get_job_set(path):
    jobset = []
    with open(path) as json_file:
        joblist = json.load(json_file)

    for job in joblist:
        jobId = job.split('.')[0]
        if jobId not in jobset:
            jobset.append(jobId)
    # job_list_len = len(joblist)
    # job_set_len = len(jobset)
    # print(f"Job list lenght: {job_list_len}")
    # print(f"Job Set lenght: {job_set_len}")

    return jobset

# Get job set
def get_exec_hosts(path):
    with open(path) as json_file:
        exec_hosts = json.load(json_file)
    return exec_hosts

def match_job_node(jobset, exechosts):
    job_node_match = []
    for jobId in jobset:
        jobId_int = int(jobId)
        job_node_dict = {'jobId': jobId_int, 'user': None, 'exechosts':[]}
        for host in exechosts:
            if host['jobList'] and jobId_int == host['jobList'][0]['id']:
                job_node_dict.update({'user': host['jobList'][0]['user']})
                host_ip = get_hostip(host['hostname'].split('.')[0])
                job_node_dict['exechosts'].append(host_ip)
        if len(job_node_dict['exechosts']) != 0:
            job_node_match.append(job_node_dict)
    return job_node_match

def get_hostip(hostname):
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None
#
# def get_hpcjobs(path):
#     with open(path) as json_file:
#         hosts = json.load(json_file)
#
#     print(f"Total jobs: {len(hosts)}")
#
#     for host in hosts:
#
#         # host name
#         print(f"hostname: {host['hostname'].split('.')[0]}")
#         hostip = get_hostip(host['hostname'].split('.')[0])
#         # host ip
#         print(f"host IP: {hostip}")
#
#         # cpu average usage
#         if host['resourceNumericValues'].get('np_load_avg') != None:
#             print(f"CPU usage: {host['resourceNumericValues']['np_load_avg']}")
#         # memory usage
#         if host['resourceNumericValues'].get('m_mem_total') != None:
#             print(f"Memory usage: {host['resourceNumericValues']['m_mem_free']}")
#
#         for job in host['jobList']:
#             if (job['masterQueue'] == "MASTER"):
#                 continue
#             jobID = job['id']
#
#             if 'taskId' in job:
#                 jobID = jobID + "-" + job['taskId']



if __name__=="__main__":
    main()
