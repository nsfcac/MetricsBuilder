from DBcm import QueryInfluxdb

def query_node(nodelist: list, config: dict, start: str, end: str, interval: str) -> dict:
    json_data = {}

    try:
        influx = QueryInfluxdb(config)
        measurement = "cluster_unified_metrics"
        fields = ["CPU1_temp", "CPU2_temp", "CPUCores", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts", "jobID"]
        
        for node in nodelist:
            json_data[node] = {}
            for field in fields:
                node_sql = node_sql_gen(field, measurement, node, start, end, interval)
                node_data = influx.get(node_sql)
                if field == "jobID":
                    for item in node_data:
                        job_list_str = item['distinct']
                        job_list = job_list_str.split(',')
                        item['distinct'] = job_list
                json_data[node][field] = node_data
 
    except Exception as err:
        print(err)

    return json_data

def query_job_set(config: dict, start: str, end: str) -> set:
    set_data = set()
    
    try: 
        influx = QueryInfluxdb(config)
        measurement = "Current_Jobs_ID"
        field = "jobs_list"

        job_list_sql = list_sql_gen(field, measurement, start, end)
        job_list_data = influx.get(job_list_sql)
        for item in job_list_data:
            job_list_str = item['distinct']
            id_list = job_list_str.split(',')
            for job_id in id_list:
                if job_id not in set_data:
                    set_data.add(job_id)
          
    except Exception as err:
        print(err)

    return set_data

def query_job_info(config: dict, joblist: list) -> dict:
    json_data = {}
    arr_fetched = {}
    try:
        influx = QueryInfluxdb(config)
        fields = ["startTime", "submitTime", "user"]

        for job_id in joblist:
            # Not an array job
            if "A" not in job_id:
                json_data[job_id] = {}
                for field in fields:
                    job_info_sql = job_sql_gen(field, job_id)
                    job_info_data = influx.get(job_info_sql)
                    json_data[job_id][fields] = job_info_data
            else:
                job_id_raw = job_id.split("A")[0]
                if job_id_raw not in arr_fetched:
                    json_data[job_id_raw] = {}
                    for field in fields:
                    job_info_sql = job_sql_gen(field, job_id)
                    job_info_data = influx.get(job_info_sql)
                    json_data[job_id_raw][fields] = job_info_data

    except Exception as err:
        print(err)

    return json_data

def node_sql_gen(field: str, measurement: str, host: str, start: str, end: str, interval: str) -> str:
    if field == "jobID":
        return("SELECT DISTINCT(" + field + ") FROM " + measurement + " WHERE host = '" + host + "' AND time >= '" + start + "' AND time <= '" + end + "'")
    else:
        return ("SELECT MAX(" + field + ") FROM " + measurement + " WHERE host = '" + host + "' AND time >= '" + start + "' AND time <= '" + end + "' GROUP BY time(" + interval + ") fill(previous)")

def list_sql_gen(field: str, measurement: str, start: str, end: str) -> list:
    return("SELECT DISTINCT(" + field + ") FROM " + measurement + " WHERE time >= '" + start + "' AND time <= '" + end + "'")

def job_sql_gen(field: str, measurement: str) -> list:
    return ("SELECT " + field + " FROM " + measurement + " ORDER BY desc LIMIT 1")