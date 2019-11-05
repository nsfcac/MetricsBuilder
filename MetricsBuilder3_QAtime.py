#! /usr/bin/python3s
import json
import re
import datetime
import time
import sys, getopt
from threading import Thread
from influxdb import InfluxDBClient
# from memory_profiler import profile


def validate_time(date_text):
    try:
        date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ")
        return date
    except ValueError as e:
        print(e)
        return False

# Get all hosts ip address
def parse_host():
    hostIp_list = []
    with open("./hostlist", 'r') as infile:
        data = infile.read()
        list_str = data[1:-1]
        list_arr = list_str.split(', ')
        for item in list_arr:
            hostName = item[1:-1]
            hostIp = hostName.split(":")[0]
            hostIp_list.append(hostIp)
    return hostIp_list

# Convert host name to ip address
def get_hostip(hostname):
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None

# @profile
def query_bmc(
        client, hostIp, measurement, measureType, 
        startTime, endTime, timeInterval
    ):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    """
    result = []

    if measurement == "CPU_Temperature":
        select_obj = (measureType + """("CPU1 Temp") as "CPU1 Temp", """
                    + measureType + """("CPU2 Temp") as "CPU2 Temp" """)
    elif measurement == "Inlet_Temperature":
        select_obj = measureType + """("Inlet Temp") as "Inlet Temp" """
    elif measurement == "CPU_Usage":
        select_obj = measureType + """("cpuusage") as "CPU Usage" """
    elif measurement == "Memory_Usage":
        select_obj = measureType + """("memoryusage") as "Memory Usage" """
    elif measurement == "Fan_Speed":
        select_obj = (measureType + """("FAN_1") as "FAN_1", """
                    + measureType + """("FAN_2") as "FAN_2", """
                    + measureType + """("FAN_3") as "FAN_3", """
                    + measureType + """("FAN_4") as "FAN_4" """)
    else:
        select_obj = measureType + """("powerusage_watts") as "Power Usage" """

    queryStr = (
        "SELECT " + select_obj
        + "FROM " + measurement 
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
    )

    try:
        influxdbQuery = client.query(queryStr)
        # print("Querying " + measureType + "data: " + measurement)
        result = list(influxdbQuery.get_points())
    except:
        pass

    return result

# @profile
def query_uge(client, hostIp, startTime, endTime, timeInterval):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    """
    result = []

    queryStr = (
        "SELECT "
        + "DISTINCT(job_data) as job_data FROM Job_Info"
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
    )

    try:
        influxdbQuery = client.query(queryStr)
        # print("Querying " + measureType + "data: " + measurement)
        result = list(influxdbQuery.get_points())
    except:
        pass

    return result

# @profile(precision=4)
def preprocess_uge(ugeMetric):
    job_list = []
    usr_list = []
    job_user_time_dic = {}

    try:
        for item in ugeMetric:
            dataStr = item["job_data"].replace("'",'"')
            job_data = json.loads(dataStr)

            nodesName = job_data["nodes"].split(",")
            jobID = job_data["jobID"]
            user = job_data["user"]
            submitTime = job_data["submitTime"]
            startTime = job_data["startTime"]

            nodesIp = []
            for node in nodesName:
                nodeIp = get_hostip(node)
                nodesIp.append(nodeIp)

            if jobID not in job_list:
                job_list.append(jobID)
                job_time_dic = {
                            jobID: {
                                "nodes": nodesIp,
                                "submitTime": submitTime,
                                "startTime": startTime,
                                "finishTime": None
                            }
                        }
                if user not in usr_list:
                    usr_list.append(jobID)
                    job_user_time_dic.update({user:[job_time_dic]})
                else:
                    job_user_time_dic[user].append(job_time_dic)
    except:
        pass
    return job_user_time_dic

# @profile(precision=4)
def get_metrics(
        client, hostIp, measure_bmc_list, 
        userJob, hostDetail,
        startTime, endTime, timeInterval, valueType
    ):
    # Get BMC metrics
    fans = []
    cpus = []
    memory = []
    cpu_temp = []
    inlet_temp = []

    # arrTemperature = [CPU1_Temp, CPU2_Temp, Inlet_Temp]
    # arrCPU_load = [CPU_Usage]
    # arrMemory_usage = [Memory_Usage]
    # arrFan_speed = [FAN_1, FAN_2, FAN_3, FAN_4]

    for item in measure_bmc_list:
        metrics = query_bmc(
            client, hostIp, item, valueType, startTime, endTime, timeInterval
        )

        length = len(metrics)

        for i in range(length):
            if item == "CPU_Temperature":
                record = [metrics[i]["CPU1 Temp"], metrics[i]["CPU2 Temp"]]
                cpu_temp.append(record)
                
            if item =="Inlet_Temperature":
                record = metrics[i]["Inlet Temp"]
                inlet_temp.append(record)

            if item == "CPU_Usage":
                record = metrics[i]["CPU Usage"]
                cpus.append(record)

            if item == "Memory_Usage":
                record = metrics[i]["Memory Usage"]
                memory.append(record)

            if item == "Fan_Speed":
                record = [metrics[i]["FAN_1"], metrics[i]["FAN_2"], metrics[i]["FAN_3"], metrics[i]["FAN_4"]]
                fans.append(record)
    
    # Merge cpu_temp with inlet_temp
    for i, item in enumerate(cpu_temp):
        item.append(inlet_temp[i])

    hostDetail.update(
        {
            hostIp: {
                "arrFan_speed": fans,
                "arrCPU_load": cpus,
                "arrMemory_usage": memory,
                "arrTemperature": cpu_temp
            }
        }
    )

    # Get UGE metrics
    uge_raw = query_uge(client, hostIp, startTime, endTime, timeInterval)
    uge_metrics = preprocess_uge(uge_raw)

    for userId, jobInfo in uge_metrics.items():
        if userId in userJob:
            userJob[userId].extend(jobInfo)
        else:
            userJob.update(
                {
                    userId: jobInfo
                }
            )
# End of get_metrics

def process_user_job(userJob):
    userJobResult = {}
    for userId, jobList in userJob.items():
        job_set = []
        agg_jobList = {}
        for job in jobList:
            jobId = list(job.keys())[0]
            jobInfo = list(job.values())[0]
            if jobId not in job_set:
                job_set.append(jobId)
                agg_jobList.update(
                    {
                        jobId: jobInfo
                    }
                )
            else:
                agg_jobList[jobId]["nodes"].extend(jobInfo["nodes"])
        userJobResult.update({ userId: agg_jobList})
    return userJobResult

def core_to_threads(
        hostIp_list, measure_bmc_list, client,
        userJob, hostDetail,
        startTime, endTime, timeInterval, valueType
    ):
    print("Pulling Metrics From InfluxDB...")

    hostIp_list_len = len(hostIp_list)
    # For progress bar
    printProgressBar(
        0, hostIp_list_len, 
        prefix = 'Progress:', suffix = 'Complete', length = 50
    )

    try:
        threads = []
        for hostIp in hostIp_list:
            a = Thread(
                target = get_metrics, 
                args = (
                    client, hostIp, measure_bmc_list, 
                    userJob, hostDetail,
                    startTime, endTime, timeInterval, valueType
                )
            )
            threads.append(a)
            a.start()
        for index, thread in enumerate(threads):
            thread.join()
            # Update Progress Bar
            printProgressBar(
                index + 1, hostIp_list_len, 
                prefix = 'Progress:', suffix = 'Complete', length = 50
            )
    except:
        pass

def run_get_metrics(
        hostIp_list, measure_bmc_list, client,
        userJob, hostDetail,
        startTime, endTime, timeInterval
    ):
    hostIp_list_len = len(hostIp_list)
    printProgressBar(
        0, hostIp_list_len, 
        prefix = 'Progress:', suffix = 'Complete', length = 50
    )
    for index, hostIp in enumerate(hostIp_list):
        get_metrics(
            client, hostIp, measure_bmc_list, 
            userJob, hostDetail,
            startTime, endTime, timeInterval
        )
        # Update Progress Bar
        printProgressBar(
            index + 1, hostIp_list_len, 
            prefix = 'Progress:', suffix = 'Complete', length = 50
        )

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

def main(argv):

    validTime = ['s', 'm', 'h', 'd', 'w']

    startTime = ""
    endTime = ""
    timeInterval = ""
    valueType = "MEAN"
    outfile = False

    try:
        opts, args = getopt.getopt(
            argv, "s:e:i:v:o:", 
            ["startTime=", "endTime=", "interval=", "valueType=", "outfile="]
        )
    except getopt.GetoptError:
        print("Arguments Error!")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--startTime"):
            startTime = arg
        elif opt in ("-e", "--endTime"):
            endTime = arg
        elif opt in ("-i", "--interval"):
            timeInterval = arg
        elif opt in ("-v", "--valueType"):
            valueType = arg
        elif opt in ("-o", "--file"):
            outfile = True
    
    print("Start time is: ", startTime)
    print("End time is: ", endTime)
    print("Time interval is: ", timeInterval)

    # Validate start and end time
    st = validate_time(startTime)
    et = validate_time(endTime)

    if not st or not et or st>et:
        return "Invalid start time and end time!\n"

    # Validate time interval
    time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
    if not time_valid.match(timeInterval):
        return "Invalid Time Interval!\n"

    # Validate value type
    if valueType not in ("MEAN", "MAX", "MIN"):
        return "Invalid Value Type!\n"

    # printlogo()
    # Set up client
    print("Set up influxDB client...")
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db'
    )

    # Get hosts Ip
    hostIp_list = parse_host()

    userJobRecord = {}

    userJob = {}
    hostDetail = {}

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]

    measure_uge_list = ["Job_Info"]

    start_time = time.time()

    core_to_threads(
        hostIp_list, measure_bmc_list, client,
        userJobRecord, hostDetail,
        startTime, endTime, timeInterval, valueType
    )

    # run_get_metrics(
    #     hostIp_list, measure_bmc_list, client,
    #     userJobRecord, hostDetail,
    #     startTime, endTime, timeInterval
    # )

    userJob = process_user_job(userJobRecord)

    returnData = {
        "timeRange": [startTime, endTime],
        "timeInterval": timeInterval,
        "hostDetail": hostDetail,
        "userJob": userJob
    }

    print("---%s seconds---" % (time.time() - start_time))

    if outfile:
        print("Writing Processed into file...")
        outfile_name = (
            "./influxdb/" + startTime + "_" 
            + endTime + "_" + timeInterval + ".json"
        )
        with open(outfile_name, "w") as outfile:
            json.dump(returnData, outfile, indent = 4, sort_keys = True)
        print("Done!")

if __name__ == "__main__":
    main(sys.argv[1:])