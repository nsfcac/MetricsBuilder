from influxdb import InfluxDBClient

class QueryInfluxdb():

    def __init__(self, config: dict) -> None:
        self.configuration = config
    
    def get(self, sql: str) -> list:
        json_data = []
        try:
            client = InfluxDBClient(**self.configuration)
            influxdbQuery = client.query(sql, epoch='s')
            json_data = list(influxdbQuery.get_points())
        except Exception as err:
            print(err)
        return json_data