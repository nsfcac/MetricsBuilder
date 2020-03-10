def process_data(json_data: dict, measurement: str) -> list:
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #         "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    try:
        for data in json_data:
            if measurement == "CPU_Temperature":
                data_point = {
                    "measurement" : "Thermal",
                    "time": data,
                    "tags": {
                        "Sensor": data,
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
            if measurement == "Inlet_Temperature":
                data_point = {
                    "measurement" : "Thermal",
                    "time": data,
                    "tags": {
                        "Sensor": "InletTemp",
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
            if measurement == "CPU_Usage":
                data_point = {
                    "measurement" : "UGE",
                    "time": data,
                    "tags": {
                        "Sensor": "CPUUsage",
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
            if measurement == "Memory_Usage":
                data_point = {
                    "measurement" : "UGE",
                    "time": data,
                    "tags": {
                        "Sensor": "MemUsage",
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
            if measurement == "Fan_Speed":
                data_point = {
                    "measurement" : "Thermal",
                    "time": data,
                    "tags": {
                        "Sensor": "FAN1",
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
            if measurement == "Node_Power_Usage":
                data_point = {
                    "measurement" : "Power",
                    "time": data,
                    "tags": {
                        "Sensor": "NodePower",
                        "NodeId": data
                    }, 
                    "fields": {
                        "Reading": data
                    }
                }
    except Exception as err:
        print(err)

