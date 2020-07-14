import re
import json
import time
import logging
from influxdb import InfluxDBClient


class JobAsyncioRequests:
    """
    Job Asyncio requests to Influxdb
    """


    def __init__(self, host: str, port: str, database: str):
        self.host = host
        self.port = port
        self.database = database
        self.data = {}
    

    def __find_jobid(self, sql:str) -> str:
        """
        Parse job id from sql string
        """
        jobid = None
        try:
            # Parse lable and node id
            jobid_pattern = "JobId='[\s\S]*'"
            jobid = re.findall(jobid_pattern, sql)[0].split("=")[1][1:-1]
        except Exception as err:
            logging.error(f"Error : Cannot parse sql string: {sql} : {err}")
        return jobid
    

    async def __fetch_json(self, sql: str, client: object) -> dict:
        """
        Get request wrapper to fetch json data from Influxdb
        """
        jobid = self.__find_jobid(sql)
        json = {}
        try:
            resp = await client.query(sql)
            series = resp['results'][0].get('series', None)
            if series:
                json = series[0]
            else:
                json = {}
                # logging.warning(f"Warning : No {label} data from {node}")
        except Exception as err:
            logging.error(f"Error : Cannot fetch job data from {jobid}")
        return {"job": jobid, "values": json}


    async def __requests(self, sqls: list) -> list:
        async with InfluxDBClient(host = self.host, port = self.port, db = self.database) as client:
            tasks = []
            for i, sql in enumerate(sqls):
                tasks.append(self.__fetch_json(sql=sql, client=client))
            return await asyncio.gather(*tasks)


    def bulk_fetch(self, sqls: list) -> list:
        self.data =  self.loop.run_until_complete(self.__requests(sqls))
        return self.data