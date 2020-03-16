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

def query_current_job(client: object) -> list:
    """
    Get Current_Job sample data
    """
    data = []
    try:
        data_sql_1 = "SELECT * FROM Current_Jobs order by time LIMIT 1"
        first = client.get(data_sql_1)
        data.extend(first)
        data_sql_2 = "SELECT * FROM Current_Jobs order by time desc LIMIT 1"
        second = client.get(data_sql_2)
        data.extend(second)
    except Exception as err:
        print(err)
    return data

def query_sample_data(client: object, measurement: str) -> list:
    """
    Get one sample data
    """
    data = []
    try:
        data_sql = "SELECT * FROM \"" + measurement + "\" LIMIT 1"
        data = client.get(data_sql)
    except Exception as err:
        print(err)
    return data

def query_data(measurement: str, client: object, start: int, end: int) -> list:
    """
    Query data from InfluxDB
    """
    result = []
    try:
        data_sql = sql_gen(measurement, start, end)
        data = client.get(data_sql)
        result.extend(data)
    except Exception as err:
        print(err)
    return result

def sql_gen(measurement: str, start: int, end: int) -> str:
    """
    Generate influxdb SQL for retriving data points during the time range
    """
    return ("SELECT * FROM " + measurement + " WHERE time >= '" + start + "' AND time < '" + end + "'")

def query_data_job(measurement: str, client: object) -> dict:
    """
    Query job info from InfluxDB
    """
    result = None
    try:
        data_sql = sql_gen_job(measurement)
        data = client.get(data_sql)
        print(data_sql)
        result = data[0]
        print("Query...........")
        print(result)
    except Exception as err:
        print(err)
    return result

def sql_gen_job(measurement: str) -> str:
    """
    Generate influxdb SQL for retriving job info
    """
    return ("SELECT * FROM \"" + measurement + "\" LIMIT 1")