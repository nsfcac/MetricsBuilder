#! /usr/bin/python3
import json
from influxdb import InfluxDBClient
from MetricsBuilder3_QAtime import query_bmc, query_uge

def main():
    # Initialization
    startTime = "2019-04-20T00:00:00Z"
    endTime = "2019-04-21T00:00:00Z"
    timeInterval = "30m"
    valueType = "MEAN"
    hostIp = "10.101.9.6"
    client = InfluxDBClient(
        host='localhost', 
        port=8086, 
        database='hpcc_monitoring_db'
    )

    measure_bmc_list = [
        "CPU_Temperature", "Inlet_Temperature", 
        "CPU_Usage", "Memory_Usage",
        "Fan_Speed", "Node_Power_Usage",
    ]
    # measure_uge_list = ["Job_Info"]

    print("Writing result into file...")
    with open("./influxdb/table.json", "w") as outfile:
        # Query BMC metrics
        # for m in measure_bmc_list:
        #    print("Get metric: {} from BMC...\n".format(m))
        #    bmc_metric = query_bmc(
        #        client, hostIp, m, valueType, startTime, endTime, timeInterval
        #    )
        #    json.dump(bmc_metric[0], outfile)
        # Query UGE metrics
        print("Get metric: Job_Info from UGE...\n")
        uge_metric = query_uge(
            client, hostIp, startTime, endTime, timeInterval
        )
        json.dump(uge_metric, outfile)
    print("Done!")

if __name__ == "__main__":
    main()
