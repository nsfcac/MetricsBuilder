import json
import flask
import re
import datetime
from flask import request
from threading import Thread
from influxdb import InfluxDBClient

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Validate start and end time 
def validate_time(date_text):
    try:
        date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%S%Z")
        return date
    except ValueError:
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

def get_metrics(
        client, hostIp, measure_bmc_list, 
        userJob, hostDetail,
        startTime, endTime, timeInterval
    ):
    # Get BMC metrics
    fans = []
    cpus = []
    memory = []
    cpu_temp = []
    inlet_temp = []

    for item in measure_bmc_list:
        max_metrics = query_bmc(
            client, hostIp, item, "MAX", startTime, endTime, timeInterval
        )

        min_metrics = query_bmc(
            client, hostIp, item, "MIN", startTime, endTime, timeInterval
        )

        avg_metrics = query_bmc(
            client, hostIp, item, "MEAN", startTime, endTime, timeInterval
        )

        length = len(max_metrics)

        for i in range(length):
            if item == "CPU_Temperature":
                record = {
                    "CPU1_Temp": {
                        "max": max_metrics[i]["CPU1 Temp"],
                        "min": min_metrics[i]["CPU1 Temp"],
                        "avg": avg_metrics[i]["CPU1 Temp"]
                    },
                    "CPU2_Temp": {
                        "max": max_metrics[i]["CPU2 Temp"],
                        "min": min_metrics[i]["CPU2 Temp"],
                        "avg": avg_metrics[i]["CPU2 Temp"]
                    }
                }
                cpu_temp.append(record)
                
            if item =="Inlet_Temperature":
                record = {
                    "max": max_metrics[i]["Inlet Temp"],
                    "min": min_metrics[i]["Inlet Temp"],
                    "avg": avg_metrics[i]["Inlet Temp"]
                }
                inlet_temp.append(record)

            if item == "CPU_Usage":
                record = {
                    "max": max_metrics[i]["CPU Usage"],
                    "min": min_metrics[i]["CPU Usage"],
                    "avg": avg_metrics[i]["CPU Usage"]
                }
                cpus.append(record)

            if item == "Memory_Usage":
                record = {
                    "max": max_metrics[i]["Memory Usage"],
                    "min": min_metrics[i]["Memory Usage"],
                    "avg": avg_metrics[i]["Memory Usage"]
                }
                memory.append(record)

            if item == "Fan_Speed":
                record = {
                    "FAN_1": {
                        "max": max_metrics[i]["FAN_1"],
                        "min": min_metrics[i]["FAN_1"],
                        "avg": avg_metrics[i]["FAN_1"]
                    },
                    "FAN_2": {
                        "max": max_metrics[i]["FAN_2"],
                        "min": min_metrics[i]["FAN_2"],
                        "avg": avg_metrics[i]["FAN_2"]
                    },
                    "FAN_3": {
                        "max": max_metrics[i]["FAN_3"],
                        "min": min_metrics[i]["FAN_3"],
                        "avg": avg_metrics[i]["FAN_3"]
                    },
                    "FAN_4": {
                        "max": max_metrics[i]["FAN_4"],
                        "min": min_metrics[i]["FAN_4"],
                        "avg": avg_metrics[i]["FAN_4"]
                    }
                }
                fans.append(record)

    hostDetail.update(
        {
            hostIp: {
                "fans": fans,
                "cpus": cpus,
                "memory": memory,
                "cpu_temp": cpu_temp,
                "inlet_temp": inlet_temp
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
        startTime, endTime, timeInterval
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
                    startTime, endTime, timeInterval
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

@app.route('/api/v1/', methods=['GET'])
def api_filter():

    validTime = ['s', 'm', 'h', 'd', 'w']
    query_parameters = request.args

    startTime = query_parameters.get('starttime')
    endTime = query_parameters.get('endtime')
    timeInterval = query_parameters.get('interval')

    # Validate start and end time
    st = validate_time(startTime)
    et = validate_time(endTime)
    if not st or not et or st>et:
        return "Invalid start time and end time"

    # Validate time interval
    time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
    if not time_valid.match(timeInterval):
        return "Invalid Time Interval"

    return "Run"

    printlogo()
    # Set up client
    print("Set up influxDB client")
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db'
    )

    hostIp_list = parse_host()

    # # hostIp = '10.101.3.53'
    # startTime = '2019-04-26T00:00:00Z'
    # endTime = '2019-04-27T00:00:00Z'
    # timeInterval = '1h'

    userJobRecord = {}

    userJob = {}
    hostDetail = {}

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]

    measure_uge_list = ["Job_Info"]

    core_to_threads(
        hostIp_list, measure_bmc_list, client,
        userJobRecord, hostDetail,
        startTime, endTime, timeInterval
    )

    userJob = process_user_job(userJobRecord)

    returnData = {
        "timeRange": [startTime, endTime],
        "timeInterval": timeInterval,
        "hostDetail": hostDetail,
        "userJob": userJob
    }

    return returnData
    # outfile_name = "./influxdb/returnData.json"
    # with open(outfile_name, "w") as outfile:
    #     json.dump(returnData, outfile, indent = 4, sort_keys = True)

app.run()