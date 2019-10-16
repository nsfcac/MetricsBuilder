import json
from influxdb import InfluxDBClient

def main():
    # Set up client
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db')

    hostIp_list = parse_host()

    hostIp = '10.101.3.53'
    startTime = '2019-04-26T00:00:00Z'
    endTime = '2019-04-26T05:00:00Z'
    timeInterval = '5m'

    userJob = {}
    hostDetail = {}

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]

    measure_uge_list = ["Job_Info"]

    get_metrics(
        client, hostIp, measure_bmc_list, 
        userJob, hostDetail,
        startTime, endTime, timeInterval
    )

    # for item in measure_bmc_list:
    #     metric = query_bmc(
    #         client, hostIp, item, "MAX", startTime, endTime, timeInterval
    #     )
    #     outfile_name = "./influxdb/" + item + ".json"
    #     with open(outfile_name, "w") as outfile:
    #         json.dump(metric, outfile, indent = 4, sort_keys = True)

    # metric = query_uge(client, startTime, endTime, timeInterval)
    # processed_metric = preprocess_uge(metric)

    outfile_name = "./influxdb/hostDetail.json"
    with open(outfile_name, "w") as outfile:
        json.dump(hostDetail, outfile, indent = 4, sort_keys = True)

def parse_host():
    hostIp_list = []
    with open("./hostlist", 'r') as infile:
        data = infile.read()
        list_str = data[1:-1]
        list_arr = list_str.split(',')
        for item in list_arr:
            hostIp = item.split(':')[0]
            hostIp_list.append(hostIp)
    return hostIp_list

def query_bmc(
        client, hostIp, measurement, measureType, 
        startTime, endTime, timeInterval
    ):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    """
    if measurement == "CPU_Temperature":
        select_obj = """("CPU1 Temp") as "CPU1 Temp","CPU2 Temp" """
    elif measurement == "Inlet_Temperature":
        select_obj = """("Inlet Temp") as "Inlet Temp" """
    elif measurement == "CPU_Usage":
        select_obj = """("cpuusage") as "CPU Usage" """
    elif measurement == "Memory_Usage":
        select_obj = """("memoryusage") as "Memory Usage" """
    elif measurement == "Fan_Speed":
        select_obj = """("FAN_1") as "FAN_1","FAN_2","FAN_3","FAN_4" """
    else:
        select_obj = """("powerusage_watts") as "Power Usage" """

    query = (
        "SELECT " + measureType + select_obj
        + "FROM " + measurement 
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
    )

    result = list(client.query(query).get_points())
    print("Querying data: " + measurement)
    return result

def query_uge(client, hostIp, startTime, endTime, timeInterval):
    query = (
        "SELECT "
        + "DISTINCT(job_data) as job_data FROM Job_Info"
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime
        + "' GROUP BY *, time(" + timeInterval + ") SLIMIT 1"
    )
    result = list(client.query(query).get_points())
    return result

def preprocess_uge(ugeMetric):
    job_list = []
    usr_list = []
    job_user_time_dic = {}

    for item in ugeMetric:
        job_data = eval(item["job_data"])
        jobID = job_data["jobID"]
        user = job_data["user"]
        submitTime = job_data["submitTime"]
        startTime = job_data["startTime"]

        if jobID not in job_list:
            job_list.append(jobID)
            job_time_dic = {
                        jobID: {
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

    return job_user_time_dic

def get_metrics(
        client, hostIp, measure_bmc_list, 
        userJob, hostDetail,
        startTime, endTime, timeInterval
    ):

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

def core_to_threads(hostIp_list):
    hostIp_list_len = len(hostIp_list)
    try:
        threads = []
        for host in hostIp_list:
            a = Thread(target = get_metrics, args = (host, userJob, hostDetail))
            threads.append(a)
            a.start()
        for index, thread in enumerate(threads):
            thread.join()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()