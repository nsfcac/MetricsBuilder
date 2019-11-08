#! /usr/bin/python3
# -*- coding: utf-8 -*-

import json
import csv
import re
import datetime
import time
import sys
import getopt

from threading import Thread
from influxdb import InfluxDBClient

from helper import *

__author__ = "Jie Li"
__copyright__ = "Copyright 2019, Texas Tech University"
__credits__ = ["Jie Li", "Ghazanfar Ali"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Jie Li"
__email__ = "jieli@ttu.edu"
__status__ = "Dev"

def validate_time(date_text):
    """Validate time string format"""
    try:
        date = datetime.datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ")
        return date
    except ValueError as e:
        print(e)
        return False

def parse_host():
    """
    Read hostlist file, extract IP addresses, 
    and return an IP addr list of monitored hosts
    """
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

def get_hostip(hostname):
    """Convert host name to IP address"""
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None

def query_bmc(
        client, hostIp, measurement, measureType, 
        startTime, endTime, timeInterval
    ):
    """
    Generate BMC query string based on the IP address, 
    startTime, endTime, and timeInterval
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
        result = list(influxdbQuery.get_points())
    except:
        result = []

    return result

def query_uge(client, hostIp, startTime, endTime, timeInterval):
    """
    Generate UGE query string based on the IP address, 
    startTime, endTime, and timeInterval
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
        result = list(influxdbQuery.get_points())
    except:
        result

    return result

def process_uge(ugeMetric):
    """Process UGE metrics"""
    timeList = []
    record = []

    for i, item in enumerate(ugeMetric):
        dataTime = item["time"]
        if dataTime not in timeList:
            timeList.append(dataTime) 
            try:
                dataStr = item["job_data"].replace("'", '"')
                job_data = json.loads(dataStr)
                new_rec = [job_data["jobID"]]
            except:
                new_rec = [[]]
            record.append(new_rec)
        else:
            for t, time in enumerate(timeList):
                if dataTime == time:
                    try:
                        dataStr = item["job_data"].replace("'", '"')
                        job_data = json.loads(dataStr)
                        if job_data["jobID"] not in record[t]:
                            record[t].append(job_data["jobID"])
                    except:
                        record[t].append([])
    return record

def preprocess_uge(ugeMetric):
    """Process UGE metrics"""
    job_list = []
    usr_list = []
    job_user_time_dic = {}

    try:
        for i, item in enumerate(ugeMetric):
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
                                "time": [submitTime, startTime, None]
                                # "submitTime": submitTime,
                                # "startTime": startTime,
                                # "finishTime": None
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
        startTime, endTime, timeInterval, valueType
    ):
    """Query BMC and UGE metrics from influxDB"""

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
        bmc_metrics = query_bmc(
            client, hostIp, item, valueType, startTime, endTime, timeInterval
        )

        bmc_length = len(bmc_metrics)

        for i in range(bmc_length):
            if item == "CPU_Temperature":
                if bmc_metrics[i]["CPU1 Temp"] and bmc_metrics[i]["CPU2 Temp"]:
                    cpu1_temp = round(float(bmc_metrics[i]["CPU1 Temp"]), 2)
                    cpu2_temp = round(float(bmc_metrics[i]["CPU2 Temp"]), 2)
                    record = [cpu1_temp, cpu2_temp]
                else:
                    record = [None, None]
                cpu_temp.append(record)
                
            if item =="Inlet_Temperature":
                if bmc_metrics[i]["Inlet Temp"]:
                    record = round(float(bmc_metrics[i]["Inlet Temp"]), 2)
                else:
                    record = None
                inlet_temp.append(record)

            if item == "CPU_Usage":
                if bmc_metrics[i]["CPU Usage"]:
                    record = round(float(bmc_metrics[i]["CPU Usage"]), 2)
                else:
                    record = None
                cpus.append(record)

            if item == "Memory_Usage":
                if bmc_metrics[i]["Memory Usage"]:
                    record = round(float(bmc_metrics[i]["Memory Usage"]), 2)
                else:
                    record = None
                memory.append(record)

            if item == "Fan_Speed":
                if bmc_metrics[i]["FAN_1"] and bmc_metrics[i]["FAN_2"] and bmc_metrics[i]["FAN_3"] and bmc_metrics[i]["FAN_4"]:
                    fan_1 = round(float(bmc_metrics[i]["FAN_1"]), 2)
                    fan_2 = round(float(bmc_metrics[i]["FAN_2"]), 2)
                    fan_3 = round(float(bmc_metrics[i]["FAN_3"]), 2)
                    fan_4 = round(float(bmc_metrics[i]["FAN_4"]), 2)
                    record = [fan_1, fan_2, fan_3, fan_4]
                else:
                    record = [None, None, None, None]
                fans.append(record)
    
    # Merge cpu_temp with inlet_temp
    for i, item in enumerate(cpu_temp):
        item.append(inlet_temp[i])

    # Get UGE metrics
    uge_metrics = query_uge(client, hostIp, startTime, endTime, timeInterval)
    uge_record = process_uge(uge_metrics)

    hostDetail.update(
        {
            hostIp: {
                "arrFan_speed": fans,
                "arrCPU_load": cpus,
                "arrMemory_usage": memory,
                "arrTemperature": cpu_temp,
                "arrJob": uge_record
            }
        }
    )
    # for i in range(uge_length):
    # uge_metrics = preprocess_uge(uge_raw)

    # for userId, jobInfo in uge_metrics.items():
    #     if userId in userJob:
    #         userJob[userId].extend(jobInfo)
    #     else:
    #         userJob.update(
    #             {
    #                 userId: jobInfo
    #             }
    #         )
# End of get_metrics

def process_user_job(userJob):
    """Process userJob information"""
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
        userJobResult.update({userId: agg_jobList})
    return userJobResult

def core_to_threads(
        hostIp_list, measure_bmc_list, client,
        userJob, hostDetail,
        startTime, endTime, timeInterval, valueType
    ):
    """Run get_metric in Multi-threads"""

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

def main(argv):

    validTime = ['s', 'm', 'h', 'd', 'w']

    startTime = ""
    endTime = ""
    timeInterval = ""
    valueType = ""
    outfile = False

    try:
        opts, args = getopt.getopt(
            argv, "s:e:i:v:o", 
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
        print("Invalid start time and end time!")
        sys.exit(2)

    # Validate time interval
    time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
    if not time_valid.match(timeInterval):
        print("Invalid Time Interval!")
        sys.exit(2)

    # Validate value type
    if valueType not in ("MEAN", "MAX", "MIN"):
        print("Invalid Value Type!")
        sys.exit(2)

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

    print("---%s seconds---" % (time.time() - start_time))

    if outfile:
        print("Writing Processed into file...")
        outfile_name = (
            "./influxdb/" + startTime + "_" 
            + endTime + "_" + timeInterval + ".csv"
        )
        build_csv(hostDetail, outfile_name)

def build_csv(json_data, outfile):
    with open(outfile, "w") as csv_file:
        hostDetail = json_data
        header_list = []
        host_list = list(hostDetail.keys())
        feature_list = list(hostDetail[host_list[0]].keys())

        csvwriter = csv.writer(csv_file)

        # Write header
        for host in host_list:
            for feature in feature_list:
                header = host + "-" + feature
                header_list.append(header)   
        
        csvwriter.writerow(header_list)

        # Write value
        timeStamp_len = len(hostDetail[host_list[0]][feature_list[0]]) - 1

        for t in range(timeStamp_len):
            each_row = []
            for host in host_list:
                for feature in feature_list:
                    try:
                        each_row.append(hostDetail[host][feature][t])
                    except:
                        each_row.append(None)
            csvwriter.writerow(each_row)

if __name__ == "__main__":
    main(sys.argv[1:])
