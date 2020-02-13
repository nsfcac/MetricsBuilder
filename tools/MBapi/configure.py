def parse_host():
    """
    Read hostlist file, extract IP addresses, 
    and return an IP addr list of monitored hosts
    """
    hostIp_list = []
    with open("./hostlist", 'r') as infile:
        data = infile.read()
        list_str = data[1:-1]
        list_arr = list_str.split(', ')
        for item in list_arr:
            hostName = item[1:-1]
            hostIp = hostName.split(":")[0]
            hostIp_list.append(hostIp)
    return hostIp_list