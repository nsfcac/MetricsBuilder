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

    # for measurement in measure_list:
    #     result = query_db(client, hostIp, measurement, startTime, endTime)
    #     for item in result:
    #         print(item)
    # measurements = client.query("SHOW MEASUREMENTS")
    # with open("./influxdb/measurements.txt", "w") as outfile:
    #     outfile.write(str(measurements))
    # print(measurements)
    for item in measure_list_viz:
        metric = query_db(
            client, hostIp, item, startTime, endTime
        )
        outfile_name = "./influxdb/" + item + ".json"
        with open(outfile_name, "w") as outfile:
            json.dump(metric, outfile, indent = 4, sort_keys = True)

    # # Select all metrics from all hosts
    # query_str = (
    #     "SELECT * FROM " + "CPU_Usage " 
    #     + "WHERE time >= '" + startTime 
    #     + "' AND time <= '" + endTime + "'"
    # )
    # metrics_all = list(client.query(query_str).get_points())

    # with open("./influxdb/CPU_all_info.json", "w") as outfile_all:
    #         json.dump(metrics_all, outfile_all, indent = 4, sort_keys = True)

def query_db(client, hostIp, measurement, startTime, endTime):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    SELECT * FROM measurement WHERE time >= *** AND time <= ***
    """
    query = (
        "SELECT * FROM " + measurement 
        + " WHERE host='" + hostIp 
        + "' AND time >= '" + startTime 
        + "' AND time <= '" + endTime + "' LIMIT 5"
    )

    # print(query)
    print("Querying data: " + measurement)
    result = list(client.query(query).get_points())

    return result

if __name__ == "__main__":
    main()