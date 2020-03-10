from datetime import datetime

def get_fst_time(client: object) -> int:
    """
    Get first time stamp of each measurement
    """
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #             "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    # sec_mea = ["cluster_unified_metrics", "Current_Jobs_ID"]

    try:            
        sql = "SELECT first(error) FROM CPU_Temperature WHERE host='10.101.1.1'"
        timestamp = client.get(sql)[0]["time"]
        print(timestamp)
        # epoch_time = int(datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f").timestamp())
        return timestamp
    except Exception as err:
        print(err)