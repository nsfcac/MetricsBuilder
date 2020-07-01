#! /usr/bin/python3
# -*- coding: utf-8 -*-

import json
import csv
import re
import time
import sys
import getopt
from datetime import datetime, timedelta

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

    # Validate the time interval and build a timedelta object
    delta = time_delta(timeInterval)
    if not delta:
        print("Invalid Time Interval!")
        sys.exit(2)

    # Validate value type
    if valueType not in ("MEAN", "MAX", "MIN"):
        print("Invalid Value Type!")
        sys.exit(2)
    
    # Generate a time list
    time_List = [dt.strftime("%Y-%m-%dT%H:%M:%SZ") for dt in datetime_range(
        st, et, delta
    )] 

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
        client, hostIp_list, time_List,
        measure_bmc_list, measure_uge_list,
        jobDetail, hostDetail,
        startTime, endTime, timeInterval, valueType
    )

    print("---%s seconds---" % (time.time() - start_time))

    if outfile:
        print("Writing Processed data into files...")
        jobfile = (
            "./CSV/JobDetail_" + startTime + "_" 
            + endTime + "_" + timeInterval + ".csv"
        )
        hostfile = (
            "./CSV/HostDetail_" + startTime + "_" 
            + endTime + "_" + timeInterval + ".csv"
        )
        build_csv(jobDetail, hostDetail, jobfile, hostfile, time_List)
        print("Done!")

def validate_time(date_text):
    """Validate time string format"""
    try:
        date = datetime.strptime(date_text, "%Y-%m-%dT%H:%M:%SZ")
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

def time_delta(timeInterval):
    """Validate time interval and generate timedelta object"""
    time_valid = re.compile('[1-9][0-9]*[s, m, h, d, w]')
    if not time_valid.match(timeInterval):
        return None
    if "s" in timeInterval:
        num = int(timeInterval.split('s')[0])
        delta = timedelta(seconds = num)
    elif "m" in timeInterval:
        num = int(timeInterval.split('m')[0])
        delta = timedelta(minutes = num)
    elif "h" in timeInterval:
        num = int(timeInterval.split('h')[0])
        delta = timedelta(hours = num)
    elif "d" in timeInterval:
        num = int(timeInterval.split('d')[0])
        delta = timedelta(days = num)
    else:
        num = int(timeInterval.split('w')[0])
        delta = timedelta(weeks = num)
    return delta

def datetime_range(start, end, interval):
    """Generate time interval array"""
    current = start
    while current < end:
        yield current
        current += interval

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
        client, hostIp, time_List,
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
        # Otherwise generate empty value for each timestamp
        else:
            for timestamp in time_List:
                if item == "CPU_Temperature":
                    CPU1_Temp.append(None)
                    CPU2_Temp.append(None)
                elif item =="Inlet_Temperature":
                    Inlet_Temp.append(None)
                elif item == "CPU_Usage":
                    CPU_Usage.append(None)
                elif item == "Memory_Usage":
                    Memory_Usage.append(None)
                elif item == "Fan_Speed":
                    Fan_1_Speed.append(None)
                    Fan_2_Speed.append(None)
                    Fan_3_Speed.append(None)
                    Fan_4_Speed.append(None)
                elif item == "Node_Power_Usage":
                    Power_Usage.append(None)
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
        client, hostIp, time_List,
        measure_uge_list,
        jobDetail, hostDetail,
        startTime, endTime, timeInterval
    ):
    """Query and process UGE metrics from influxDB"""
    # These variables are used to generate a list of jobs 
    # running on the host for each timestamp
    Jobs = []
    Node_Jobs = {}

    for item in measure_uge_list:
        uge_metrics = query_uge(
            client, hostIp, item, startTime, endTime, timeInterval
        )
        uge_length = len(uge_metrics)
        # If query_uge returns a valid result
        if uge_metrics: 
            for i in range(uge_length):
                # uge metrics may contains several points with the same timestamp
                timestamp = uge_metrics[i]["time"]
                if item == "Job_Info":
                    try:
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
                        
                        # Generate job-info pairs, the info includes information
                        # about user, submit time and start time
                        if jobID not in jobDetail:
                            jobDetail.update(
                                {
                                    jobID: job_Info
                                }
                            )
                    except:
                        # Otherwise job_data is not a valid string
                        jobID = None

                    if timestamp not in Node_Jobs:
                        Node_Jobs.update(
                            {
                                timestamp: [jobID]
                            }
                        )
                    else:
                        if jobID not in Node_Jobs[timestamp]:
                            Node_Jobs[timestamp].append(jobID)
        # Otherwise generate empty value for each timestamp
        else:
            for timestamp in time_List:
                Node_Jobs.update(
                    {
                        timestamp: None
                    }
                )

    # Process job list for each timestamp
    for time in time_List:
        Jobs.append(Node_Jobs[time])
    
    # Update hostDetail:
    if hostIp in hostDetail:
        hostDetail[hostIp].update(
            {
                "Jobs": Jobs,
            }
        )
    else:
        hostDetail.update(
            {
                hostIp: {
                    "Jobs": Jobs,
                }
            }
        )
    
    return None

def core_to_threads(
        client, hostIp_list, time_List,
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
                    client, hostIp, time_List,
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
                    client, hostIp, time_List,
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

def build_csv(jobDetail, hostDetail, jobfile, hostfile, time_List):
    """Convert json files to CSV files"""
    # Write host details into a CSV file
    with open(hostfile, "w") as host_csv_file:
        header_list = ["TimeStamp"]
        host_list = list(hostDetail.keys())
        feature_list = list(hostDetail[host_list[0]].keys())

        csvwriter = csv.writer(host_csv_file)

        # Write header
        for host in host_list:
            for feature in feature_list:
                header = host + "-" + feature
                header_list.append(header)   
        
        csvwriter.writerow(header_list)

        # Write value
        for i, timestamp in enumerate(time_List):
            each_row = [timestamp]
            for host in host_list:
                for feature in feature_list:
                    each_row.append(hostDetail[host][feature][i])
            csvwriter.writerow(each_row)
    
    # Write job details into a CSV file
    with open(jobfile, "w") as job_csv_file:
        header_list = ["JobID"]
        job_list = list(jobDetail.keys())
        feature_list = list(jobDetail[job_list[0]].keys())

        csvwriter = csv.writer(job_csv_file)
        # Write header
        for feature in feature_list:
            header_list.append(feature)
        
        csvwriter.writerow(header_list)

        # Write value
        for job in job_list:
            each_row = [job]
            for feature in feature_list:
                each_row.append(jobDetail[job][feature])
            csvwriter.writerow(each_row)

if __name__ == "__main__":
    main(sys.argv[1:])
