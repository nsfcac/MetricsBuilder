import json
import time
import datetime
import requests
import warnings
from collections import Counter
from  threading import Thread

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    node_pwr_list = {}


    print("Pulling Metrics From BMC...")

    #######################################################
    # Get exec hosts and fetch corresponding power usuage #
    #######################################################
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    if exec_hosts != None:
        exechost_list = get_exechosts_ip(exec_hosts)
        core_to_threads(exechost_list, node_pwr_list, conn_time_out, read_time_out, session)
        # print(node_pwr_list)
    else:
        print("No Execution Host")
        return

    #########################
    # Get current timestamp #
    #########################
    timestamp = datetime.datetime.now().ctime()

    print("Pulling Metrics From UGE...")

    host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")

    if host_summary != None:
        node_job_match, job_set = match_node_job(host_summary)
    else:
        print("Get Host Summary Error")
        return

    job_user_time_dic = match_job_user_time(job_set, host_summary)

    job_pwr_list = calc_job_pwr(node_job_match, job_set, node_pwr_list, job_user_time_dic)

    # print(json.dumps(job_pwr_list, indent = 4, sort_keys = True))
    # print(len(job_set))

    # uge_tasklist = ['jobs', 'hostsummary']
    # uge_results = {'jobs': None, 'hostsummary': None}
    # uge_errors = {'jobs': None, 'hostsummary': None}
    #
    # # For progress bar
    # task_len = len(uge_tasklist)
    # printProgressBar(0, task_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #
    # # Get job list, host summary
    # for index, task in enumerate(uge_tasklist):
    #     uge_results[task], uge_errors[task] = get_uge_info(conn_time_out, read_time_out, session, task)
    #     printProgressBar(index + 1, task_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
    #
    # job_list = uge_results['jobs']
    # host_summary = uge_results['hostsummary']

    print("Interleaving Metrics ...")

    # if job_list != None and host_summary != None:
    #     job_set = get_job_set(job_list)
    #     job_node_match = match_job_node(job_set, host_summary)
    # else:
    #     print(err_info)
    #     return

    # print("Job list length: ")，
    # print(len(job_set))

    # Get exec hosts power usage for each job
    # for i, item in enumerate(job_node_match):
    #     pwr_usage_tot = 0
    #     pwr_usage = []
    #     for exechost in item['ExecHosts']:
    #         # print(node_pwr_list[exechost])
    #         # if node_pwr_list[exechost] != None:
    #         pwr_usage.append(node_pwr_list[exechost])
    #         try:
    #             pwr_usage_tot = pwr_usage_tot + node_pwr_list[exechost]
    #         except TypeError:
    #             pwr_usage_tot = None
    #
    #     item.update({'PowerConsumedWatts': pwr_usage, 'TotalPowerConsumedWatts': pwr_usage_tot, 'TimeStamp': timestamp})
    #
    # print("Writing log files...")

    with open("./uge/JobPwr.json", "w") as outfile_jobpwr:
            json.dump(job_pwr_list, outfile_jobpwr, indent = 4, sort_keys = True)

    with open("./uge/HostJob.json", "w") as outfile_hostjob:
            json.dump(node_job_match, outfile_hostjob, indent = 4, sort_keys = True)
    #
    # with open("./uge/JobList.json", "w") as outfile_joblist:
    #         json.dump(job_list, outfile_joblist, indent = 4, sort_keys = True)
    #
    # with open("./uge/JobSetSorted.json", "w") as outfile_jobset:
    #         json.dump(sorted(job_set), outfile_jobset, indent = 4, sort_keys = True)
    #
    # with open("./uge/HostSummary.json", "w") as outfile_hostsum:
    #         json.dump(host_summary, outfile_hostsum, indent = 4, sort_keys = True)
    #
    # with open("./interleaved/jobNodePower.json", "w") as outfile:
    #         json.dump(job_node_match, outfile, indent = 4, sort_keys = True)
    #
    # print("Done!")

    # print(json.dumps(job_node_match, indent = 4, sort_keys = True))


# Get exec hosts list of ip addresses
def get_exechosts_ip(exechosts):
    exechost_list = []
    for exechost in exechosts:
        host_ip = get_hostip(exechost.split('.')[0])
        if host_ip != None:
            exechost_list.append(host_ip)
    return exechost_list

# Match host and jobs
def match_node_job(host_summary):
    node_job_match = []
    job_set = []
    for host in host_summary:
        host_job = {}
        job_list = []
        core_used = 0
        host_job.update({'HostIp': get_hostip(host['hostname'].split('.')[0]), 'Counting': None})
        for job in host['jobList']:
            job_list.append(job['id'])
            if job['id'] not in job_set:
                job_set.append(job['id'])
        host_job.update({'Counting': Counter(job_list).most_common()})
        for item in host_job['Counting']:
            core_used += item[1]
        host_job.update({'CoreUsed': core_used})
        node_job_match.append(host_job)
    return node_job_match, job_set

def match_job_user_time(job_set, host_summary):
    job_user_time_dic = {}
    for index, job in enumerate(job_set):
        for host in host_summary:
            if job == host['jobList']['id']:
                job_user_time_dic[job] = {'user': host['jobList']['user'], 'startTime': host['jobList']['startTime']}
                continue
    return job_user_time_dic


# Calculate PowerConsumedWatts for each Job
def calc_job_pwr(node_job_match, job_set, node_pwr_list, job_user_time_dic):
    job_pwr_list = []
    for index, job in enumerate(job_set):
        job_pwr_dict = {'User': job_user_time_dic[job]['user'],'JobId': job, 'StartTime': job_user_time_dic[job]['startTime'],'ExecHosts':[], 'OccupationPct': [], 'PowerConsumedWatts': [], 'TotalPowerConsumedWatts': None}
        total_pwr = 0
        for node in node_job_match:
            for i in node['Counting']:
                if job == i[0]:
                    node_ip = node['HostIp']
                    pwr_pct = round(i[1]/node['CoreUsed'], 2)
                    try:
                        pwr_each = round(pwr_pct * node_pwr_list[node_ip], 2)
                    except TypeError:
                        pwr_each = 0
                    total_pwr += pwr_each
                    job_pwr_dict['ExecHosts'].append(node_ip)
                    job_pwr_dict['OccupationPct'].append(pwr_pct)
                    job_pwr_dict['PowerConsumedWatts'].append(pwr_each)
        job_pwr_dict.update({'TotalPowerConsumedWatts': round(total_pwr, 2)})
        job_pwr_list.append(job_pwr_dict)

    return job_pwr_list


# # Build job-node matches
# def match_job_node(job_set, host_summary):
#
#     # For progress bar
#     job_set_len = len(job_set)
#     printProgressBar(0, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
#
#     job_node_match = []
#     for index, jobId in enumerate(job_set):
#         jobId_int = int(jobId)
#         job_node_dict = {'JobId': jobId_int, 'User': None, 'StartTime': None, 'ExecHosts':[], 'LoadAvg':[], 'MemUsed': [], 'TotalMemUsed': None }
#         mem_total = 0
#         for host in host_summary:
#             if host['jobList'] and jobId_int == host['jobList'][0]['id']:
#                 job_node_dict.update({'User': host['jobList'][0]['user'], 'StartTime': host['jobList'][0]['startTime']})
#                 host_ip = get_hostip(host['hostname'].split('.')[0])
#                 mem_used = host['hostValues']['mem_used']
#                 job_node_dict['ExecHosts'].append(host_ip)
#                 job_node_dict['LoadAvg'].append(host['hostValues']['load_avg'])
#                 job_node_dict['MemUsed'].append(mem_used)
#                 mem_total = mem_total + float(mem_used.split('G')[0])
#         if len(job_node_dict['ExecHosts']) != 0:
#             job_node_match.append(job_node_dict)
#         mem_total_str = str(round(mem_total,1)) + 'G'
#         job_node_dict.update({'TotalMemUsed': mem_total_str})
#         printProgressBar(index + 1, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
#     return job_node_match

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
        # print("Request Power Usage Error")
        node_pwr_list.update({host: None})

# Use multi-thread to fetch Power Usuage from each exec host
def core_to_threads(exec_hosts, node_pwr_list, conn_time_out, read_time_out, session):

    # For progress bar
    exec_hosts_len = len(exec_hosts)
    printProgressBar(0, exec_hosts_len, prefix = 'Progress:', suffix = 'Complete', length = 50)

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
            printProgressBar(index + 1, exec_hosts_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
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
