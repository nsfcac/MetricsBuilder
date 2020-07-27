import yaml


def parse_config() -> object:
    """
    Read configuration file
    """
    cfg = []
    try:
        with open('openapi_server/controllers/config.yml', 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        return cfg
    except Exception as err:
        print(err)


def parse_nodelist(nodelist_cfg: list) -> list:
    """
    Generate ip addresses of nodes from the configuration
    """
    nodelist = []
    for item in nodelist_cfg:
        ip_addr_node = item.split("[")[0]
        ip_addr_subnet = item.split("[")[1]

        sections = ip_addr_subnet[:-1].split(",")
        for section in sections:
            if "-" in section:
                st = int(section.split("-")[0])
                ed = int(section.split("-")[1])
                for i in range(st, ed+1):
                    ip_addr = ip_addr_node + str(i)
                    nodelist.append(ip_addr)
            else:
                ip_addr = ip_addr_node + str(int(section))
                nodelist.append(ip_addr)
    
    return nodelist


def read_nodelist(nodelist: str, node_pool: list) -> list:
    """
    Parse user specified nodelist
    """
    node_list = []
    user_nodelist = []
    try:
        nodelist = nodelist.split(", ")
        user_nodelist = parse_nodelist(nodelist)
        node_list = [node for node in user_nodelist if node in node_pool]
    except Exception as err:
        print(err)
    return node_list


def read_metrics(metrics: list, metrics_pool: dict) -> dict:
    """
    Parse user specified metrics
    """
    measurements = {}
    try:
        for metric in metrics:
            if metric in metrics_pool:
                measurements.update({
                    metric: metrics_pool[metric]
                })
    except Exception as err:
        print(err)
    return measurements