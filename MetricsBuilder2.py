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
    # measure_list = [
    #     "Current_Jobs_ID", "Current_Users", 
    #     "Job_Info", "node_job_info", 
    #     "system_metrics", "Cluster_Nodes_Jobs_PWR_Usage", 
    #     "Node_Power_Usage", "Node_Power_State", 
    #     "CPU_Usage", "Memory_Usage", 
    #     "Fan_Speed", "CPU_Temperature", "Inlet_Temperature", 
    #     "BMC_Health", "Inlet_Health", "Node_Health", "CPU_Health", 
    #     "Memory_Health", "Fan_Health", "Node_LED_Indicator"
    # ]

    # host_measure_list = [
    #     "BMC_Health", "CPU_Health", "CPU_Temperature", 
    #     "CPU_Usage", "Fan_Health", "Fan_Speed", "Inlet_Health",
    #     "Inlet_Temperature", "Job_Info", "Memory_Health",
    #     "Memory_Usage", "Node_Health", "Node_LED_Indicator",
    #     "Node_Power_State", "Node_Power_Usage"
    # ]

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
        
    ]

    measure_uge_list = ["Job_Info"]

    for item in measure_bmc_list:
        metric = query_bmc(
            client, hostIp, item, "MAX", startTime, endTime, timeInterval
        )
        outfile_name = "./influxdb/" + item + ".json"
        with open(outfile_name, "w") as outfile:
            json.dump(metric, outfile, indent = 4, sort_keys = True)

def query_bmc(client, hostIp, measurement, measureType, startTime, endTime, timeInterval):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    SELECT * FROM measurement WHERE time >= *** AND time <= ***
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

    # print(query)
    result = list(client.query(query).get_points())

    print("Querying data: " + measurement)

    return result

if __name__ == "__main__":
    main()