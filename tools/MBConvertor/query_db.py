def get_fst_time(client: object) -> object:
    """
    Get first time stamp of each measurement
    """
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #             "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    # sec_mea = ["cluster_unified_metrics", "Current_Jobs_ID"]

    try:            
        field = "CPU1 Temp"
        measurement = "CPU_Temperature"
        host = "10.101.1.1"
        sql = "SELECT first('" + field + "') FROM " + measurement + "WHERE host = '" + host + "'"
        data_point = client.get(sql)
        return data_point
    except Exception as err:
        print(err)