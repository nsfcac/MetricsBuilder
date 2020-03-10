from influxdb import InfluxDBClient

class QueryInfluxdb():

    def __init__(self, config: dict) -> None:
        self.configuration = config
        self.client = InfluxDBClient(**self.configuration)
    
    def get(self, sql: str) -> list:
        json_data = []
        try:
            influxdbQuery = self.client.query(sql, epoch='ms')
            json_data = list(influxdbQuery.get_points())
        except Exception as err:
            print(err)
        return json_data

    def write(self, json_data: object) -> None:
        try:
            self.client.write_points(json_data)
        except Exception as err:
            print(err)