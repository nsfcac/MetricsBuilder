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

    measure_list_viz = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
        "Job_Info"
    ]

    # for item in measure_list_viz:
    #     metric = query_db(
    #         client, hostIp, item, startTime, endTime, timeInterval
    #     )
    #     outfile_name = "./influxdb/" + item + ".json"
    #     with open(outfile_name, "w") as outfile:
    #         json.dump(metric, outfile, indent = 4, sort_keys = True)

    query = """SELECT MAX("CPU1 Temp") as "CPU1 Temp", "CPU2_Temp" FROM CPU_Temperature WHERE host='10.101.3.53'AND time >= '2019-04-26T00:00:00Z' AND time <= '2019-04-26T05:00:00Z' GROUP BY *, time(5m) SLIMIT 1"""
    result = list(client.query(query).get_points())
    with open("./influxdb/max_sample.json", "a") as outfile:
        json.dump(result, outfile, indent = 4, sort_keys = True)

    # query = "SELECT * FROM Inlet_Temperature WHERE host='10.101.3.53'AND time >= '2019-04-26T00:00:00Z' AND time <= '2019-04-26T05:00:00Z' LIMIT 1"
    # result = list(client.query(query).get_points())
    # with open("./influxdb/sample.json", "a") as outfile:
    #     json.dump(result, outfile, indent = 4, sort_keys = True)

def query_db(client, hostIp, measurement, startTime, endTime, timeInterval):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    SELECT * FROM measurement WHERE time >= *** AND time <= ***
    """
    if measurement == "CPU_Temperature":
        tag_name = "CPU1 Temp"
    elif measurement == "Inlet_Temperature":
        tag_name = "Inlet Temp"
    elif measurement == "CPU_Usage":
        tag_name = "cpuusage"
    elif measurement == "Memory_Usage":
        tag_name = "memoryusage"
    elif measurement == "Fan_Speed":
        tag_name = "FAN_1"
    elif measurement == "Node_Power_Usage":
        tag_name = "powerusage_watts"
    else:
        tag_name = "job_data"

    query = (
        "SELECT * "
        # + tag_name
        + "FROM " + measurement 
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime + "'"
        # + "' GROUP BY time(" + timeInterval + "),* SLIMIT 1"
    )

    # print(query)
    result = list(client.query(query).get_points())

    print("Querying data: " + measurement)
    print("--length: " + len(result))

    return result

if __name__ == "__main__":
    main()