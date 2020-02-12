from DBcm import QueryInfluxdb

def query_node(nodelist: list, config: dict, start: str, end: str, interval: str) -> dict:
    json_data = {}
    try:
        influx = QueryInfluxdb(config)
        measurement = "cluster_unified_metrics"
        fields = ["CPU1_temp", "CPU2_temp", "CPUCores", "cpuusage", "fan1_speed", "fan2_speed", "fan3_speed", "fan4_speed", "inlet_temp", "jobID", "memoryusage", "powerusage_watts"]
        
        for node in nodelist:
            json_data[node] = {}
            for field in fields:
                node_sql = node_sql_gen(field, measurement, node, start, end, interval)
                node_data = influx.get(node_sql)
                if field == "jobID":
                    for index, item in enumerate(node_data):
                        node_data[index] = item.split('_')[1] 
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
        for id_str in job_list_data:
            id_list = id_str.split(',')
            for job_id in id_list:
                # if job is an array job
                if "A" in job_id:
                    this_job_id = job_id.split("A")[0]
                    if this_job_id not in set_data:
                        set_data.add(this_job_id)
                else:
                    if job_id not in set_data:
                        set_data.add(job_id)
                
    except Exception as err:
        print(err)

    return set_data

def query_job_info(config: dict, joblist: list) -> dict:
    json_data = {}
    try:
        influx = QueryInfluxdb(config)
        fields = ["startTime", "submitTime", "user"]

        for job in joblist:
            job_id = job.split("_")[1]
            json_data[job_id] = {}
            for field in fields:
                job_info_sql = job_sql_gen(field, job)
                job_info_data = influx.get(job_info_sql)
                json_data[job_id][fields] = job_info_data

    except Exception as err:
        print(err)

    return json_data

def node_sql_gen(field: str, measurement: str, host: str, start: str, end: str, interval: str) -> str:
    return ("SELECT MAX(" + field + ") FROM " + measurement + " WHERE host = " + host + " AND " + "time >= '" + start + "' AND time <= '" + end + "' GROUP BY time(" + interval + ")")

def list_sql_gen(field: str, measurement: str, start: str, end: str) -> list:
    return("SELECT DISTINCT(" + field + ") FROM " + measurement + " WHERE time >= '" + start + "' AND time <= '" + end + "'")

def job_sql_gen(field: str, measurement: str) -> list:
    return ("SELECT " + filed + " FROM " + measurement + " ORDER BY desc LIMIT 1")