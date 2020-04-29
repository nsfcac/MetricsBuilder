import yaml

def parse_conf()-> object:
    """
    Read configuration file
    """
    cfg = []
    try:
        with open('./config.yml', 'r') as ymlfile:
        # with open('openapi_server/controllers/config.yml', 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
    except Exception as err:
        print(err)
    return cfg


def parse_host() -> list:
    """
    Read hostlist file, extract IP addresses, 
    and return an IP addr list of monitored hosts
    """
    hostIp_list = []
    try:
        with open("./hostlist", 'r') as infile:
        # with open("openapi_server/controllers/hostlist", 'r') as infile:
            data = infile.read()
            list_str = data[1:-1]
            list_arr = list_str.split(', ')
            for item in list_arr:
                hostName = item[1:-1]
                hostIp = hostName.split(":")[0]
                hostIp_list.append(hostIp)
    except Exception as err:
        print(err)
    return hostIp_list