import json
import time
import datetime
import requests
import warnings
from  threading import Thread

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    node_pwr_list = {}


    print("Pulling Metrics From BMC...")

    # Get exec hosts and fetch corresponding power usuage
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    if exec_hosts != None:
        exechost_list = get_exechosts_ip(exec_hosts)
        core_to_threads(exechost_list, node_pwr_list, conn_time_out, read_time_out, session)
        # print(node_pwr_list)
    else:
        print("No Executing Host")
        return

    timestamp = datetime.datetime.now().isoformat()

    print("Pulling Metrics From UGE...")
    # Get job list, exechosts, host summary
    job_list, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")

    if job_list != None and host_summary != None:
        job_set = get_job_set(job_list)
        job_node_match = match_job_node(job_set, host_summary)
    else:
        print(err_info)
        return

    print("Interleaving Metrics ...")
    # Get exec hosts power usage for each job
    for item in job_node_match:
        pwr_usage_tot = 0
        pwr_usage = []
        for exechost in item['ExecHosts']:
            # print(node_pwr_list[exechost])
            if node_pwr_list[exechost] != None:
                pwr_usage.append(node_pwr_list[exechost])
                pwr_usage_tot = pwr_usage_tot + node_pwr_list[exechost]
            else:
                pwr_usage.append(None)
                pwr_usage_tot = None
        item.update({'PowerConsumedWatts': pwr_usage, 'TotalPowerConsumedWatts': pwr_usage_tot, 'TimeStamp': timestamp})

    with open("jobNodePower.json", "wb") as outfile:
            json.dump(job_node_match, outfile, indent = 4, sort_keys = True)

    print("Done...")

    # print(json.dumps(job_node_match, indent = 4, sort_keys = True))


# Get exec hosts list of ip addresses
def get_exechosts_ip(exechosts):
    exechost_list = []
    for exechost in exechosts:
        host_ip = get_hostip(exechost.split('.')[0])
        if host_ip != None:
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

# Build job-node matches
def match_job_node(jobset, host_summary):
    job_node_match = []
    for jobId in jobset:
        jobId_int = int(jobId)
        job_node_dict = {'JobId': jobId_int, 'User': None, 'ExecHosts':[]}
        for host in host_summary:
            if host['jobList'] and jobId_int == host['jobList'][0]['id']:
                job_node_dict.update({'User': host['jobList'][0]['user']})
                host_ip = get_hostip(host['hostname'].split('.')[0])
                job_node_dict['ExecHosts'].append(host_ip)
        if len(job_node_dict['ExecHosts']) != 0:
            job_node_match.append(job_node_dict)
    return job_node_match

# Convert host name to ip address
def get_hostip(hostname):
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None

# Get UGE information
def get_uge_info(conn_time_out, read_time_out, session, type):

    passwordUrl = "http://129.118.104.35:8182/"
    if type == "jobs" or type == "users" or type == "exechosts":
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

# Get Power Usuage
def get_powerusage(host, node_pwr_list, conn_time_out, read_time_out, session):
    try:
        url = "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Power/"
        response = session.get(url, verify = False, auth = ('password', 'monster'), timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()

        node_pwr_list.update({host: data['PowerControl'][0]['PowerConsumedWatts']})

    except requests.exceptions.RequestException as e:
        print("Request Power Usage Error")
        node_pwr_list.update({host: None})

# Use multi-thread to fetch Power Usuage from each exec host
def core_to_threads(exec_hosts, node_pwr_list, conn_time_out, read_time_out, session):

    # For progress bar
    l = len(exec_hosts)
    printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50)

    warnings.filterwarnings('ignore', '.*', UserWarning,'warnings_filtering',)
    try:
        threads = []
        for host in exec_hosts:
            a = Thread(target = get_powerusage, args = (host, node_pwr_list, conn_time_out, read_time_out, session, ))
            threads.append(a)
            a.start()
        for index, thread in enumerate(threads):
            thread.join()
            # Update Progress Bar
            printProgressBar(index + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50)
    except Exception as e:
        print(e)

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print()

if __name__ == "__main__":
    main()
