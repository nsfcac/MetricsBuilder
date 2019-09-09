import json
import requests

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    # Get job list, exechosts, host summary
    job_list, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")

    if job_list != None and exec_hosts != None and host_summary != None:
        job_set = get_job_set(job_list)
        exechost_list = get_exechosts_ip(exec_hosts)
        job_node_match = match_job_node(job_set, host_summary)

        # with open("jobnode.json", "wb") as outfile:
        #         json.dump(job_node_match, outfile, indent = 4)
        # print(job_node_match)
        print(exechost_list)
    else:
        print(err_info)

# Get exec hosts ip addr
def get_exechosts_ip(exechosts):
    exechost_list = []
    for exechost in exechosts:
        host_ip = get_hostip(exechost.split('.')[0])
        exechost_list.append(host_ip)
    return exechost_list

# Get job set
def get_job_set(joblist):
    jobset = []
    for job in joblist:
        jobId = job.split('.')[0]
        if jobId not in jobset:
            jobset.append(jobId)

    return jobset

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

def get_uge_info(conn_time_out, read_time_out, session, type):

    passwordUrl = "http://129.118.104.35:8182/"
    if type == "jobs":
        url = passwordUrl + type
    elif type == "users":
        url = passwordUrl + type
    elif type == "exechosts":
        url = passwordUrl + type
    elif type == "hostsummary":
        url = passwordUrl + "hostsummary/1/500"
    else:
        return None, "UGE API ERROR"

    try:
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()
        return data, str(None)

    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

if __name__ == "__main__":
    main()
