#! /usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import getopt
from datetime import datetime, timedelta

from influxdb import InfluxDBClient

__author__ = "Jie Li"
__copyright__ = "Copyright 2019, Texas Tech University"
__credits__ = ["Jie Li"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Jie Li"
__email__ = "jieli@ttu.edu"
__status__ = "Dev"

def main(argv):

    startTime = ""
    endTime = ""
    dbname = ""

    try:
        opts, args = getopt.getopt(
            argv, "s:e:d:vh",
            ["startTime=", "endTime=", "version", "help"]
        )
    except getopt.GetoptError:
        print("Arguments Error!")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-s", "--startTime"):
            startTime = arg
        elif opt in ("-e", "--endTime"):
            endTime = arg
        elif opt in ("-d", "--database"):
            dbname = arg
        elif opt in ("-v", "--version"):
            print(__version)
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
    
    # Validata database name
    if len(database) == 0:
        print("Please a database name!")
        sys.exit(2)
        
    if database == "hpcc_monitoring_db":
        print("Please use another database name!")
        sys.exit(2)
    
    # Set up client
    print("Set up influxDB client...")
    client = InfluxDBClient(
        host='localhost', 
        port=8086
    )

    client.switch_database('hpcc_monitoring_db')

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

    # Todo fetch all points

    # Create database
    client.create_database(dbname)

    return

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
    with open("../hostlist", 'r') as infile:
        data = infile.read()
        list_str = data[1:-1]
        list_arr = list_str.split(', ')
        for item in list_arr:
            hostName = item[1:-1]
            hostIp = hostName.split(":")[0]
            hostIp_list.append(hostIp)
    return hostIp_list

def query_bmc(
        client, hostIp, measurement, startTime, endTime
    ):
    """
    Generate BMC query string based on the IP address, startTime, endTime
    """
    result = None

    if measurement == "CPU_Temperature":
        select_obj = ("""("CPU1 Temp") as "CPU1 Temp", """
                    + """("CPU2 Temp") as "CPU2 Temp" """)
    elif measurement == "Inlet_Temperature":
        select_obj = """("Inlet Temp") as "Inlet Temp" """
    elif measurement == "CPU_Usage":
        select_obj = """("cpuusage") as "CPU Usage" """
    elif measurement == "Memory_Usage":
        select_obj = """("memoryusage") as "Memory Usage" """
    elif measurement == "Fan_Speed":
        select_obj = ("""("FAN_1") as "FAN_1", """
                    + """("FAN_2") as "FAN_2", """
                    + """("FAN_3") as "FAN_3", """
                    + """("FAN_4") as "FAN_4" """)
    elif measurement == "Node_Power_Usage":
        select_obj = """("powerusage_watts") as "Power Usage" """
    else:
        print(measurement + " is not in the database!")
        return result

    queryStr = (
        "SELECT " + select_obj
        + "FROM " + measurement 
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "'"
    )

    try:
        influxdbQuery = client.query(queryStr)
        result = list(influxdbQuery.get_points())
    except:
        print(e)

    return result

def query_uge(
        client, hostIp, measurement, 
        startTime, endTime
    ):
    """
    Generate UGE query string based on the IP address, 
    startTime, endTime
    """
    result = None

    # measure_uge_list = ["Job_Info"]
    if measurement == "Job_Info":
        queryStr = (
            "SELECT job_data FROM Job_Info"
            + " WHERE host='" + hostIp 
            + "' AND time >= '" + startTime 
            + "' AND time <= '" + endTime
            + "'"
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

def printHelp():
    print(
    """
    Options:
    --version, -v       Show version number                             [boolean]
    --startTime, -s     Specify start time of monitoring data           [string]
    --endTime, -e       Specify end time of monitoring data             [string]
    --database, -d      Specify newly added database name               [string]
    --help, -h          Show help                                       [boolean]
    """)

if __name__ == "__main__":
    main(sys.argv[1:])