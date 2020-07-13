import re
import json
import time
import logging
import asyncio
import asyncio
from aioinflux import InfluxDBClient


class AsyncioRequests:
    """
    Asyncio requests to Influxdb
    """
    import asyncio


    def __init__(self, host: str, port: str, db: str, meas: str):
        self.host = host
        self.port = port
        self.db = db
        self.meas = meas
        self.data = {}
        self.loop = self.asyncio.get_event_loop()
    

    def __find_label_node(self, sql:str) -> str:
        """
        Parse Label and node from sql string
        """
        label = None
        node = None
        try:
            pattern = "Label='[\s\S]*'"
            label_node_str = re.findall(pattern, sql)[0]
            label_node_str.split("'")
            label = label_node_str[1]
            node = label_node_str[3]
        except:
            logging.error(f"Error : Cannot parse sql string: {sql}")
        return (label, node)
    
    async def __fetch_json(self, sql: str, client: object) -> dict:
        """
        Get request wrapper to fetch json data from Influxdb
        """
        try:
            resp = await client.query(sql)
            series = resp['results'][0].get('series', None)
            (label, node) = self.__find_label_node(sql)
            if series:
                json = series[0]
            else:
                json = {}
                # logging.warning(f"Warning : No data from {node} : {sql}")
            return {"node": node, "label": label, "data": json}
        except:
            logging.error(f"Error : Cannot fetch data from: {sql}")


    async def __requests(self, sqls: list) -> list:
        async with InfluxDBClient(host = self.host, port = self.port, db = self.db) as client:
            tasks = []
            for i, sql in enumerate(sqls):
                tasks.append(self.__fetch_json(sql=sql, client=client))
            return await self.asyncio.gather(*tasks)


    def bulk_fetch(self, sqls: list) -> list:
        self.data =  self.loop.run_until_complete(self.__requests(sqls))
        self.loop.close()
        return self.data