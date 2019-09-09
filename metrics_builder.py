import json

def main():
    job_set = get_job_set("joblist.json")
    hostsummary = get_hostsummary("hostsummary.json")
    job_node_match = match_job_node(job_set, hostsummary)

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

    return jobset

# Get job set
def get_hostsummary(path):
    with open(path) as json_file:
        hostsummary = json.load(json_file)
    return hostsummary

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

if __name__=="__main__":
    main()
