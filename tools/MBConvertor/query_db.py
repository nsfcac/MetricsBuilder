def get_fst_time(client: object) -> object:
    """
    Get first time stamp of each measurement
    """
    # fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
    #             "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
    # sec_mea = ["cluster_unified_metrics", "Current_Jobs_ID"]

    try:            
        sql = """ SELECT first("CPU1 Temp") FROM "CPU_Temperature" WHERE host="10.101.1.1" """
        data_point = client.get(sql)
        return data_point
    except Exception as err:
        print(err)