from DBcm import QueryInfluxdb

def query_db(config: dict, start: str, end: str, interval: str) -> dict:
    json_data = {}
    influx = QueryInfluxdb(config)
    node_mea = 'cluster_unified_metrics'
    jobs_mea = 'Current_Jobs_ID'

    node_sql = str_generator(node_mea, start, end, interval)
    node_data = influx.get(node_sql)
    json_data['node_data'] = node_data

    jobs_sql = str_generator(jobs_mea, start, end, interval)
    jobs_id = influx.get(jobs_sql)
    json_data['jobs_id'] = jobs_id
    
    return json_data

def str_generator(mea: str, start: str, end: str, interval: str) -> str:
    return ("SELECT * FROM " + mea + " WHERE time >= '" + start + "' AND time <= '" + end + "' GROUP BY *, time(" + interval + ") SLIMIT 1")