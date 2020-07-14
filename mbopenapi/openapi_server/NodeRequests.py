import re
import json
import time
import logging
from influxdb import InfluxDBClient


class NodeRequests:
    """
    Node Asyncio requests to Influxdb
    """


    def __init__(self, host: str, port: str, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.data = []
    

    def __find_label_node(self, sql:str) -> str:
        """
        Parse Label and node from sql string
        """
        node = None
        measurement = None
        label = None
        try:
            # Parse measurement
            meas_pattern = "FROM [a-zA-Z]* WHERE"
            measurement = re.findall(meas_pattern, sql)[0].split(' ')[1]

            # Parse lable and node id
            label_node_pattern = "Label='[\s\S]*'"
            label_node_str = re.findall(label_node_pattern, sql)[0].split("'")
            label = label_node_str[1]
            node = label_node_str[3]
        except Exception as err:
            logging.error(f"Error : Cannot parse sql string: {sql} : {err}")
        return (node, measurement, label)
    

    def __fetch_json(self, sql: str, client: object) -> dict:
        """
        Get request wrapper to fetch json data from Influxdb
        """
        (node, measurement, label) = self.__find_label_node(sql)
        json = {}
        try:
            resp = client.query(sql).get_points()
            # series = resp['results'][0].get('series', None)
            # if series:
            #     json = series[0]['values']
            # else:
            #     json = {}
                # logging.warning(f"Warning : No {label} data from {node}")
        except Exception as err:
            logging.error(f"Error : Cannot fetch {measurement} - {label} data from {node}")
        return {"node": node, "measurement": measurement, "label": label, "values": resp}


    def bulk_fetch(self, sqls: list) -> list:
        with InfluxDBClient(host = self.host, port = self.port, database = self.database) as client:
            for i, sql in enumerate(sqls):
                sql_data = self.__fetch_json(sql, client)
                self.data.append(sql_data)
        return self.data