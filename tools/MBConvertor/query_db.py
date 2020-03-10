def get_fst_time(influx: object) -> object:
    """
    Get first time stamp
    """
    try:
        sql = "SELECT first('CPU1 Temp') FROM 'CPU_Temperature' WHERE host='10.101.1.1'"
        data_point = influx.get(sql)
        return data_point
    except Exception as err:
        print(err)