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

def main(argv):

    validTime = ['s', 'm', 'h', 'd', 'w']

    startTime = ""
    endTime = ""
    timeInterval = ""
    valueType = ""
    outfile = False

    try:
        opts, args = getopt.getopt(
            argv, "s:e:i:t:ovh", 
            ["startTime=", "endTime=", "interval=", "valueType=", "outfile", "version", "help"]
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
        elif opt in ("-t", "--valueType"):
            valueType = arg
        elif opt in ("-o", "--file"):
            outfile = True
        elif opt in ("-v", "--version"):
            print(__version__)
            return
        elif opt in ("-h", "--help"):
            printHelp()
            return

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

    printLogo()

    # Set up client
    print("Set up influxDB client...")
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db'
    )

    # Get hosts Ip
    hostIp_list = parse_host()

    # BMC metrics list
    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]
    # UGE metrics list
    measure_uge_list = ["Job_Info"]

    jobDetail = {}
    hostDetail = {}

    # Record running time of core_to_threads
    start_time = time.time()

    # Get metrics using multi-thread
    core_to_threads(
        client, hostIp_list, 
        measure_bmc_list, measure_uge_list,
        jobDetail, hostDetail,
        startTime, endTime, timeInterval, valueType
    )

    print("---%s seconds---" % (time.time() - start_time))

    if outfile:
        print("Writing Processed into file...")
        outfile1_name = (
            "./influxDB/jobDetail" + startTime + "_" 
            + endTime + "_" + timeInterval + ".json"
        )
        with open(outfile1_name, "w") as outfile1:
            json.dump(jobDetail, outfile1, indent = 4, sort_keys = True)
        
        outfile2_name = (
            "./influxDB/hostDetail" + startTime + "_" 
            + endTime + "_" + timeInterval + ".json"
        )
        with open(outfile2_name, "w") as outfile2:
            json.dump(hostDetail, outfile2, indent = 4, sort_keys = True)

        print("Done!")

    # if outfile:
    #     print("Writing Processed into file...")
    #     outfile_name = (
    #         "./influxDB/" + startTime + "_" 
    #         + endTime + "_" + timeInterval + ".csv"
    #     )
    #     build_csv(hostDetail, outfile_name)

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
    result = None

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
    elif measurement == "Node_Power_Usage":
        select_obj = measureType + """("powerusage_watts") as "Power Usage" """
    else:
        print(measurement + " is not in the database!")
        return result

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
        print(e)

    return result

def query_uge(
        client, hostIp, measurement, 
        startTime, endTime, timeInterval
    ):
    """
    Generate UGE query string based on the IP address, 
    startTime, endTime, and timeInterval
    """
    result = None

    # measure_uge_list = ["Job_Info"]
    if measurement == "Job_Info":
        queryStr = (
            "SELECT "
            + "DISTINCT(job_data) as job_data FROM Job_Info"
            + " WHERE host='" + hostIp 
            + "' AND time >= '" + startTime 
            + "' AND time <= '" + endTime
            + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
        )
    else:
        print(measurement + " is not in the database!")
        return result

    try:
        influxdbQuery = client.query(queryStr)
        result = list(influxdbQuery.get_points())
    except:
        print(e)

    return result

def get_bmc_metrics(
        client, hostIp, 
        measure_bmc_list,
        hostDetail,
        startTime, endTime, timeInterval, valueType
    ):
    """Query and process BMC metrics from influxDB"""

    # BMC metrics
    CPU1_Temp = []
    CPU2_Temp = []
    Inlet_Temp = []
    CPU_Usage = []
    Memory_Usage = []
    Fan_1_Speed = []
    Fan_2_Speed = []
    Fan_3_Speed = []
    Fan_4_Speed = []
    Power_Usage = []

    for item in measure_bmc_list:
        bmc_metrics = query_bmc(
            client, hostIp, item, valueType, startTime, endTime, timeInterval
        )

        # If query_bmc returns a valid result
        if bmc_metrics:
            bmc_length = len(bmc_metrics)

            for i in range(bmc_length):
                if item == "CPU_Temperature":
                    try:
                        cpu1_temp = round(float(bmc_metrics[i]["CPU1 Temp"]), 2)
                        cpu2_temp = round(float(bmc_metrics[i]["CPU2 Temp"]), 2)
                    except:
                        cpu1_temp = None
                        cpu2_temp = None

                    CPU1_Temp.append(cpu1_temp)
                    CPU2_Temp.append(cpu2_temp)
                    
                elif item =="Inlet_Temperature":
                    try:
                        inlet_temp = round(float(bmc_metrics[i]["Inlet Temp"]), 2)
                    except:
                        inlet_temp = None

                    Inlet_Temp.append(inlet_temp)

                elif item == "CPU_Usage":
                    try:
                        cpu_usage = round(float(bmc_metrics[i]["CPU Usage"]), 2)
                    except:
                        cpu_usage = None

                    CPU_Usage.append(cpu_usage)

                elif item == "Memory_Usage":
                    try:
                        memory_usage = round(float(bmc_metrics[i]["Memory Usage"]), 2)
                    except:
                        memory_usage = None

                    Memory_Usage.append(memory_usage)

                elif item == "Fan_Speed":
                    try:
                        fan_1 = round(float(bmc_metrics[i]["FAN_1"]), 2)
                        fan_2 = round(float(bmc_metrics[i]["FAN_2"]), 2)
                        fan_3 = round(float(bmc_metrics[i]["FAN_3"]), 2)
                        fan_4 = round(float(bmc_metrics[i]["FAN_4"]), 2)
                    except:
                        fan_1 = None
                        fan_2 = None
                        fan_3 = None
                        fan_4 = None
                        
                    Fan_1_Speed.append(fan_1)
                    Fan_2_Speed.append(fan_2)
                    Fan_3_Speed.append(fan_3)
                    Fan_4_Speed.append(fan_4)

                elif item == "Node_Power_Usage":
                    try:
                        power_usage = round(float(bmc_metrics[i]["Power Usage"]), 2)
                    except:
                        power_usage = None

                    Power_Usage.append(power_usage)

                else:
                    print(item + " is not in the database!")

    # Update hostDetail
    if hostIp in hostDetail:
        hostDetail[hostIp].update(
            {
                "CPU1_Temp": CPU1_Temp,
                "CPU2_Temp": CPU2_Temp,
                "Inlet_Temp": Inlet_Temp,
                "CPU_Usage": CPU_Usage,
                "Memory_Usage": Memory_Usage,
                "Fan_1_Speed": Fan_1_Speed,
                "Fan_2_Speed": Fan_2_Speed,
                "Fan_3_Speed": Fan_3_Speed,
                "Fan_4_Speed": Fan_4_Speed,
                "Power_Usage": Power_Usage
            }
        )
    else:
        hostDetail.update(
            {
                hostIp: {
                    "CPU1_Temp": CPU1_Temp,
                    "CPU2_Temp": CPU2_Temp,
                    "Inlet_Temp": Inlet_Temp,
                    "CPU_Usage": CPU_Usage,
                    "Memory_Usage": Memory_Usage,
                    "Fan_1_Speed": Fan_1_Speed,
                    "Fan_2_Speed": Fan_2_Speed,
                    "Fan_3_Speed": Fan_3_Speed,
                    "Fan_4_Speed": Fan_4_Speed,
                    "Power_Usage": Power_Usage
                }
            }
        )
    return None

def get_uge_metrics(
        client, hostIp, 
        measure_uge_list,
        jobDetail, hostDetail,
        startTime, endTime, timeInterval
    ):
    """Query and process UGE metrics from influxDB"""
    # These variables are used to generate a list of jobs 
    # running on the host for each timestamp
    Jobs = []
    Node_Jobs = {}
    Time_List = []

    for item in measure_uge_list:
        uge_metrics = query_uge(
            client, hostIp, item, startTime, endTime, timeInterval
        )
        # If query_uge returns a valid result
        if uge_metrics:
            uge_length = len(uge_metrics)

            for i in range(uge_length):
                if item == "Job_Info":
                    try:
                        timestamp = uge_metrics[i]["time"]
                        # Replace ' to "", otherwise json.loads won't work
                        dataStr = uge_metrics[i]["job_data"].replace("'",'"')
                        job_data = json.loads(dataStr)

                        jobID = job_data["jobID"]
                        user = job_data["user"]
                        submitTime = job_data["submitTime"]
                        startTime = job_data["startTime"]
                        job_Info = {
                            "user": user,
                            "submitTime": submitTime,
                            "startTime": startTime
                        }

                        # The timestamp list records all the timestamps 
                        # being read, since uge_query returns several points 
                        # under the same timestamp, we have to aggregate them
                        if timestamp not in Time_List:
                            Time_List.append(timestamp)
                            Node_Jobs.update(
                                {
                                    timestamp: [jobID]
                                }
                            )
                        else:
                            if jobID not in Node_Jobs[timestamp]:
                                Node_Jobs[timestamp].append(jobID)
                        
                        # Generate job-info pairs, the info includes information
                        # about user, submit time and start time
                        if jobID not in jobDetail:
                            jobDetail.update(
                                {
                                    jobID: job_Info
                                }
                            )
                    except:
                        pass

    # Process job list for each timestamp
    for time in Time_List:
        Jobs.append(Node_Jobs[time])
    
    # Update hostDetail:
    if hostIp in hostDetail:
        hostDetail[hostIp].update(
            {
                "Jobs": Jobs,
                "time": Time_List
            }
        )
    else:
        hostDetail.update(
            {
                hostIp: {
                    "Jobs": Jobs,
                    "time": Time_List
                }
            }
        )
    
    return None

def core_to_threads(
        client, hostIp_list, 
        measure_bmc_list, measure_uge_list,
        jobDetail, hostDetail,
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
        bmc_threads = []
        uge_threads = []
        for hostIp in hostIp_list:
            # BMC threads
            bmc = Thread(
                target = get_bmc_metrics, 
                args = (
                    client, hostIp, 
                    measure_bmc_list,
                    hostDetail,
                    startTime, endTime, timeInterval, valueType
                )
            )
            bmc_threads.append(bmc)
            bmc.start()
            # UGE threads
            uge = Thread(
                target = get_uge_metrics, 
                args = (
                    client, hostIp, 
                    measure_uge_list,
                    jobDetail, hostDetail,
                    startTime, endTime, timeInterval
                )
            )
            uge_threads.append(uge)
            uge.start()

        for i in range(hostIp_list_len):
            bmc_threads[i].join()
            uge_threads[i].join()
            # Update Progress Bar
            printProgressBar(
                i + 1, hostIp_list_len, 
                prefix = 'Progress:', suffix = 'Complete', length = 50
            )
    except:
        pass

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
