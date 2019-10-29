#! /usr/bin/python3s
import json
import re
import datetime
import time
import sys, getopt
from threading import Thread

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

def query_bmc(
        queryStrAll, hostIp, measurement, measureType, 
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

    queryStrAll = queryStrAll + "; " + queryStr

def query_uge(queryStrAll, hostIp, startTime, endTime, timeInterval):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    """
    queryStr = (
        "SELECT "
        + "DISTINCT(job_data) as job_data FROM Job_Info"
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
    )

    queryStrAll = queryStrAll + "; " + queryStr

def core_to_threads(
        hostIp_list, measure_bmc_list, queryStrAll,
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
                    queryStrAll, hostIp, measure_bmc_list, 
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

def main(argv):

    validTime = ['s', 'm', 'h', 'd', 'w']

    startTime = ""
    endTime = ""
    timeInterval = ""

    try:
        opts, args = getopt.getopt(argv, "s:e:i:", ["startTime=", "endTime=", "intervla="])
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

    # printlogo()

    # Get hosts Ip
    hostIp_list = parse_host()

    queryStrAll = ""

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]

    measure_uge_list = ["Job_Info"]

    core_to_threads(
        hostIp_list, measure_bmc_list, queryStrAll,
        userJobRecord, hostDetail,
        startTime, endTime, timeInterval
    )
    
    with open("./qprofScripts.txt", "w") as queryStrings:
        queryStrings.write(queryStrAll)

    
if __name__ == "__main__":
    main(sys.argv[1:])
