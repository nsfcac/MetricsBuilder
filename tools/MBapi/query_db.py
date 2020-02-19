def query_info(node_list: list, influx: object, start: str, end: str, interval: str, value: str) -> dict:
    json_data = {}

    node_data = query_node_info(node_list, influx, start, end, interval, value)

    job_list = query_job_list(influx, start, end)
    job_data = query_job_info(influx, job_list)

    json_data.update({
        "node_data": node_data,
        "job_data": job_data
    })

    return json_data

def query_node_info(node_list: list, influx: object, start: str, end: str, interval: str, value: str) -> dict:
    """
    Query node information
    """
    # should configurable
    json_data = {}

    try:
        measurement = "cluster_unified_metrics"
        fields = ["CPU1_temp", "CPU2_temp", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts"]
        
        for node in node_list:
            json_data[node] = {}
            for field in fields:
                node_sql = node_sql_gen(field, measurement, node, start, end, interval, value)
                node_data = influx.get(node_sql)
                # jobID is stored as string in influxdb
                if field == "jobID":
                    for item in node_data:
                        job_list_str = item['distinct']
                        job_list = job_list_str.split(',')
                        item['distinct'] = job_list
                json_data[node][field] = node_data
 
    except Exception as err:
        print(err)

    return json_data

def query_job_list(influx: object, start: str, end: str) -> list:
    # Get all jobs running during the time range, should configurable
    job_set = set()
    
    try: 
        measurement = "Current_Jobs_ID"
        field = "jobs_list"

        job_list_sql = list_sql_gen(field, measurement, start, end)
        job_list_data = influx.get(job_list_sql)
        for item in job_list_data:
            job_list_str = item['distinct']
            id_list = job_list_str.split(',')
            for job_id in id_list:
                if job_id not in job_set:
                    job_set.add(job_id)
          
    except Exception as err:
        print(err)
    
    job_list = list(job_set)

    return job_list

def query_job_info(influx: object, job_list: list) -> dict:
    """
    Query job information
    """
    json_data = {}
    try:
        fields = ["startTime", "submitTime", "user"]
        # fields = ["start_time", "submit_time", "user_name", "finish_time"]

        for job_id in job_list:
            json_data[job_id] = {}
            job_info_sql = job_sql_gen(job_id)
            job_info_data = influx.get(job_info_sql)
            for field in fields:
                if field == "startTime":
                    re_field = "start_time"
                elif field == "submitTime":
                    re_field = "submit_time"
                else:
                    re_field = "user_name"
                json_data[job_id][re_field] = job_info_data[0][field]

    except Exception as err:
        print(err)

    return json_data

def node_sql_gen(field: str, measurement: str, host: str, start: str, end: str, interval: str, value: str) -> str:
    """
    Generate influxdb SQL for retriving metrics from 'cluster_unified_metrics'
    """
    if field == "jobID":
        return("SELECT DISTINCT(jobID) FROM " + measurement + " WHERE host = '" + host + "' AND time >= '" + start + "' AND time < '" + end + "' GROUP BY time(" + interval + ") fill(null)")
    else:
        return ("SELECT " + value + "(" + field + ") FROM " + measurement + " WHERE host = '" + host + "' AND time >= '" + start + "' AND time < '" + end + "' GROUP BY time(" + interval + ")")

def list_sql_gen(field: str, measurement: str, start: str, end: str) -> list:
    """
    Generate influxdb SQL for retriving jobs running during the time range
    """
    return("SELECT DISTINCT(" + field + ") FROM " + measurement + " WHERE time >= '" + start + "' AND time < '" + end + "'")

def job_sql_gen(measurement: str) -> list:
    return ("SELECT * FROM " + measurement + " ORDER BY desc LIMIT 1")