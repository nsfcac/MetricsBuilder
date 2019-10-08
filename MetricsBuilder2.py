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
    measure_list = ["node_job_info", "Node_Power_State", "Node_Power_Usage", 
                "Cluster_Nodes_Jobs_PWR_Usage", "BMC_Health", "Inlet_Health", 
                "Node_Health", "CPU_Health", "Memory_Health", "Fan_Health",
                "CPU_Usage", "Memory_Usage", "Fan_Speed", "CPU_Temperature", 
                "Inlet_Temperature", "Node_LED_Indicator"]

    for measurement in measure_list:
        result = query_db(client, hostIp, measurement, startTime, endTime)
        for item in result:
            print(item)

def query_db(client, hostIp, measurement, startTime, endTime):
    """Generate query string based on the ip address, 
    startTime and endTime(time range)
    SELECT * FROM measurement WHERE time >= *** AND time <= ***
    """
    query = ("SELECT * FROM " + measurement 
             + " WHERE host='" + hostIp 
             + "' AND time >= '" + startTime 
             + "' AND time <= '" + endTime + "' LIMIT 1")

    # print(query)
    print("Querying data: " + measurement)
    result = client.query(query).get_points()

    return result

if __name__ == "__main__":
    main()