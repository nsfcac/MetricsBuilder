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
        
    
    async def __fetch_json(self, sql: str, node: str, client: object) -> dict:
        """
        Get request wrapper to fetch json data from Influxdb
        """
        try:
            resp = await client.query(sql)
            return await {"node": node, "data": resp}
        except:
            # logging.error(f"Error : Cannot fetch data from {node} : {sql}")
            return {"node": node, "data": {}}


    async def __requests(self, sqls: list, nodes: list) -> list:
        async with InfluxDBClient(host = self.host, port = self.port, db = self.db) as client:
            tasks = []
            for i, sql in enumerate(sqls):
                tasks.append(self.__fetch_json(sql=sql, node=nodes[i], client=client))
            return await self.asyncio.gather(*tasks)


    def bulk_fetch(self, sqls: list, nodes: list) -> list:
        self.data =  self.loop.run_until_complete(self.__requests(sqls, nodes))
        self.loop.close()
        return self.data