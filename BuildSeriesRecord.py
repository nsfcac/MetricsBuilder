import json
import time
import datetime
import requests
import warnings
from collections import Counter
from threading import Thread
from threading import Timer
from time import sleep

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def main():
    all_record = []

    oneEntry = fetch_data(all_record)
    all_record.append(oneEntry)
    # rt = RepeatedTimer(60, interleave, all_record)

    # try:
    #     fetch_data(all_record)
    #     sleep(600) # your long-running job goes here...
    # finally:
    #     rt.stop() # better in a try/finally block to make sure the program ends!

    with open("./records/records_10mins.json", "w") as outfile:
            json.dump(all_record, outfile, indent = 4)

def fetch_data(all_record):
    time_stamp = datetime.datetime.now().ctime()

    result = {
        "time": time_stamp, "jobHost": None, 
        "userJob": None, "hostDetail": None
    }

    conn_time_out = 15
    read_time_out = 40
    session = requests.Session()

    # Get HostSummary metrics from UGE API
    host_summary, err_info = get_uge_info(
        conn_time_out, read_time_out, session, "hostsummary"
    )
    ## UGE DETAILS
    host_uge_detail = preprocess_uge(host_summary)

    # Get BMC metrics from redfish API
    bmc_info = {}
    exec_hosts, err_info = get_uge_info(
        conn_time_out, read_time_out, session, "exechosts"
    )

    if exec_hosts == None:
        print("No Execution Host")
        return
    else:
        exechost_list = get_exechosts_ip(exec_hosts)

        get_bmc_threads(
            exechost_list, bmc_info, conn_time_out, read_time_out, session
        )
    ## BMC DETAILS
    host_bmc_detail = preprocess_bmc(bmc_info)

    # Aggregate data
    merge_data = merge(host_uge_detail, host_bmc_detail)

    return merge_data

def preprocess_uge(host_summary):
    host_uge_detail = {}
    for host in host_summary:
        hostIp = get_hostip(host["hostname"].split('.')[0])
        cpus = host["hostValues"]["load_avg"]
        memory = host["hostValues"]["mem_used"].split('G')[0]
        host_uge_detail.update({hostIp: {"cpus": cpus, "memory": memory}})
    return host_uge_detail

# Use multi-thread to fetch Power Usuage from each exec host
def get_bmc_threads(exec_hosts, bmc_info, conn_time_out, read_time_out, session):

    print("-Pulling Metrics From BMC...")
    # For progress bar
    exec_hosts_len = len(exec_hosts)
    printProgressBar(
        0, exec_hosts_len, prefix = 'Progress:', 
        suffix = 'Complete', length = 50
    )

    warnings.filterwarnings(
        'ignore', '.*', UserWarning,'warnings_filtering',
    )
    try:
        threads = []
        for host in exec_hosts:
            a = Thread(
                target = get_bmc, 
                args = (host, bmc_info, conn_time_out, read_time_out, session, )
                )
            threads.append(a)
            a.start()
        for index, thread in enumerate(threads):
            thread.join()
            # Update Progress Bar
            printProgressBar(
                index + 1, exec_hosts_len, 
                prefix = 'Progress:', suffix = 'Complete', length = 50
            )
    except Exception as e:
        print(e)

def get_bmc(host, bmc_info, conn_time_out, read_time_out, session):
    try:
        return_data = {"power": None, "thermal": None}

        # Fetch power data
        url = ( 
            "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Power/"
        )
        response = session.get(
            url, verify = False, 
            auth = ('password', 'monster'), 
            timeout = (conn_time_out, read_time_out)
        )
        response.raise_for_status()
        data = response.json()
        return_data.update({"power": data})

        # Fetch thermal data
        url = (
            "https://" + host + "/redfish/v1/Chassis/System.Embedded.1/Thermal/"
        )
        response = session.get(
            url, verify = False, 
            auth = ('password', 'monster'), 
            timeout = (conn_time_out, read_time_out)
        )
        response.raise_for_status()
        data = response.json()
        return_data.update({"thermal": data})

        # Update bmc_info
        print(f"BMC: ", host)
        bmc_info.update({host: return_data})

    except requests.exceptions.RequestException as e:
        # print("Request Power Usage Error")
        bmc_info.update({host: {"power": None, "thermal": None}})

def preprocess_bmc(bmc_info):
    host_bmc_detail = {}
    for key, value in bmc_info.items():

        fans = []
        temperature = []
        if "Fans" in value and "Temperatures" in value:
            for fan in value["thermal"]["Fans"]:
                fan_detail = {}
                if "Name" in fan and "Status" in fan and "Reading" in fan:
                    fan_detail.update({"name": fan["Name"]})
                    health_status = str_to_int(fan["Status"]["Health"])
                    fan_detail.update({"health": health_status})
                    fan_detail.update({"speed": fan["Reading"]})
                fans.append(fan_detail)
            
            for temp in value["thermal"]["Temperatures"]:
                temp_detail = {}
                if "Name" in temp and "Status" in temp and "ReadingCelsius" in temp:
                    temp_detail.update({"name": temp["Name"]})
                    health_status = str_to_int(temp["Status"]["Health"])
                    temp_detail.update({"health": health_status})
                    temp_detail.update({"temp": temp["ReadingCelsius"]})
                temperature.append(temp_detail)

        host_bmc_detail.update({key:{"fans": fans, "temperature": temperature}})

    return host_bmc_detail

# Convert status string to intger
def str_to_int(status):
    value = 0
    if status == "OK":
        value = 0
    elif status == "Cirtical":
        value = 1
    # Warning
    else:
        value = -1
    return value

# Merge metrics from uge and bmc
def merge(host_uge_detail, host_bmc_detail):
    hostDetail = {}
    for key, value in host_uge_detail.items():
        host = {"fans": None, "cpus": None, "memory": None, "temperature": None}
        if key in host_bmc_detail:
            host["fans"] = host_bmc_detail[key]["fans"]
            host["cpus"] = value["cpus"]
            host["memory"] = value["memory"]
            host["temperature"] = host_bmc_detail[key]["temperature"]
        hostDetail.update({key: host})
    return hostDetail

def interleave(record_list):

    result = {"TimeStamp": None, "JobList": []}

    #########################
    # Get current timestamp #
    #########################

    time_stamp = datetime.datetime.now().ctime()

    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    printlogo()

    node_pwr_list = {}

    #######################
    # Get exection hosts #
    #######################
    print("-Getting Exection Host List...")
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")

    if exec_hosts == None:
        print("No Execution Host")
        return
    else:
        exechost_list = get_exechosts_ip(exec_hosts)

        core_to_threads(exechost_list, node_pwr_list, conn_time_out, read_time_out, session)
        # print(node_pwr_list)

    print("-Pulling Metrics From UGE...")

    host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")

    if host_summary != None:
        node_job_match, job_set = match_node_job(host_summary)
    else:
        print("Get Host Summary Error")
        return

    ######################
    # Interleave metrics #
    ######################
    job_user_time_dic = match_job_user_time(job_set, host_summary)

    job_pwr_list = calc_job_pwr(node_job_match, job_set, node_pwr_list, job_user_time_dic, time_stamp)

    print("-Total Running Jobs on Qunanh Cluster: ", end =" ")
    print(len(job_pwr_list))

    job_core_pwr = build_job_core_pwr(job_pwr_list)

    result.update({"TimeStamp": time_stamp, "JobList": job_core_pwr})

    record_list.append(result)



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

    print("-Preprocessing UGE Metrics ...")
    # For progress bar
    job_set_len = len(job_set)
    printProgressBar(0, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)

    job_user_time_dic = {}
    for index, jobId in enumerate(job_set):
        for host in host_summary:
            flag = 0
            for job in host['jobList']:
                if jobId == job['id']:
                    job_user_time_dic[jobId] = {'user': job['user'], 'startTime': job['startTime']}
                    flag = 1
                    continue
            if flag == 1:
                continue
        printProgressBar(index + 1, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)
    return job_user_time_dic


# Calculate PowerConsumedWatts for each Job
def calc_job_pwr(node_job_match, job_set, node_pwr_list, job_user_time_dic, time_stamp):

    job_pwr_list = []

    print("-Interleaving Power Metrics ...")
    # For progress bar
    job_set_len = len(job_set)
    printProgressBar(0, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)

    for index, job in enumerate(job_set):
        job_pwr_dict = {'TimeStamp': time_stamp,'User': job_user_time_dic[job]['user'],'JobId': job, 'StartTime': job_user_time_dic[job]['startTime'],'ExecCores':None, 'ExecHosts':[], 'OccupationPct': [], 'PowerConsumedWatts': [], 'TotalPowerConsumedWatts': None}
        total_pwr = 0
        total_cores = 0
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
                    total_cores += i[1]
                    job_pwr_dict['ExecHosts'].append(node_ip)
                    job_pwr_dict['OccupationPct'].append(pwr_pct)
                    job_pwr_dict['PowerConsumedWatts'].append(pwr_each)
        job_pwr_dict.update({'ExecCores':total_cores, 'TotalPowerConsumedWatts': round(total_pwr, 2)})
        job_pwr_list.append(job_pwr_dict)
        printProgressBar(index + 1, job_set_len, prefix = 'Progress:', suffix = 'Complete', length = 50)

    return job_pwr_list

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

    print("-Pulling Metrics From BMC...")
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

# Build job-core-power dict
def build_job_core_pwr(job_pwr_list):
    result_list = []
    for job in job_pwr_list:
        host_len = len(job['ExecHosts'])
        job_core_pwr_dict = {"JobId": job['JobId'], "ExecCores": job['ExecCores'], "ExecHosts": host_len, "Power": job['TotalPowerConsumedWatts']}
        result_list.append(job_core_pwr_dict)
    return result_list

# Export data for pyplot
def pyplot(job_pwr_list):
    job_id = []
    job_no_nodes = []
    job_pwr = []
    for job in job_pwr_list:
        job_id.append(job['JobId'])
        job_no_nodes.append(len(job['ExecHosts']))
        job_pwr.append(job['TotalPowerConsumedWatts'])
    return job_id, job_no_nodes, job_pwr

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

def printlogo():
    print("""    __  ___     __       _           ____        _ __    __          """)
    print("""   /  |/  /__  / /______(_)_________/ __ )__  __(_) /___/ /__  _____ """)
    print("""  / /|_/ / _ \/ __/ ___/ / ___/ ___/ __  / / / / / / __  / _ \/ ___/ """)
    print(""" / /  / /  __/ /_/ /  / / /__(__  ) /_/ / /_/ / / / /_/ /  __/ /     """)
    print("""/_/  /_/\___/\__/_/  /_/\___/____/_____/\__,_/_/_/\__,_/\___/_/      """)


if __name__ == "__main__":
    main()
