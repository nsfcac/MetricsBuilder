from datetime import datetime

def get_phase_time(client: object) -> int:
    """
    Get first time stamp of each measurement
    """
    phase_time = []

    try:            
        phase1_start_sql = "SELECT first(error) FROM CPU_Temperature WHERE host='10.101.1.1'"
        phase2_start_sql = "SELECT first(cpuusage) FROM cluster_unified_metrics WHERE host='10.101.1.1'"

        phase1_start = client.get(phase1_start_sql)[0]["time"]
        phase_time.append(phase1_start)

        phase2_start = client.get(phase2_start_sql)[0]["time"]
        phase_time.append(phase2_start)

    except Exception as err:
        print(err)
    
    return phase_time

# fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
#             "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
# sec_mea = ["cluster_unified_metrics", "Current_Jobs_ID"]


def query_data_point(client: object) -> list:
    """
    Get one sample data
    """
    data = []
    try:
        data_sql = "SELECT * FROM CPU_Temperature WHERE host='10.101.1.1' LIMIT 1"
        data = client.get(data_sql)
    except Exception as err:
        print(err)
    return data

def query_data(node_list: list, measurement: str, 
               client: object, start: int, end: int) -> list:
    """
    Query data from InfluxDB
    """
    result = []
    try:
        for node in node_list:
            data_sql = sql_gen(measurement, node, start, end)
            data = client.get(data_sql)
            result.extend(data)
    except Exception as err:
        print(err)
    return result

def sql_gen(measurement: str, host: str, start: int, end: int) -> str:
    """
    Generate influxdb SQL for retriving data points during the time range
    """
    return("SELECT * FROM " + measurement + " WHERE host = '" + host + "' AND time >= '" + start + "' AND time < '" + end + "'")