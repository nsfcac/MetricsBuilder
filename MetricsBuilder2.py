import json
from influxdb import InfluxDBClient

def main():
    # Set up client
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db')

    hostIp = '10.101.3.53'
    startTime = '2019-04-26T00:00:00Z'
    endTime = '2019-04-26T05:00:00Z'
    timeInterval = '5m'

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]

    measure_uge_list = ["Job_Info"]

    # for item in measure_bmc_list:
    #     metric = query_bmc(
    #         client, hostIp, item, "MAX", startTime, endTime, timeInterval
    #     )
    #     outfile_name = "./influxdb/" + item + ".json"
    #     with open(outfile_name, "w") as outfile:
    #         json.dump(metric, outfile, indent = 4, sort_keys = True)

    metric = query_uge(client, startTime, endTime, timeInterval)
    processed_metric = preprocess_uge(metric)

    outfile_name = "./influxdb/userJob.json"
    with open(outfile_name, "w") as outfile:
        json.dump(processed_metric, outfile, indent = 4, sort_keys = True)

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

def query_uge(client, startTime, endTime, timeInterval):
    query = (
        "SELECT "
        + "DISTINCT(job_data) as job_data FROM Job_Info"
        + " WHERE time >= '" + startTime 
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

if __name__ == "__main__":
    main()