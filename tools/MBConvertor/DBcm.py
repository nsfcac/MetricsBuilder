from influxdb import InfluxDBClient

class QueryInfluxdb():

    def __init__(self, config: dict) -> None:
        self.configuration = config
        self.client = InfluxDBClient(**self.configuration)

    def list_measurement(self) -> list:
        tables = []
        try:
            tables = self.client.get_list_measurements()
        except Exception as err:
            print(err)
        return tables


    def get(self, sql: str) -> list:
        json_data = []
        try:
            influxdbQuery = self.client.query(sql, epoch='s')
            json_data = list(influxdbQuery.get_points())
        except Exception as err:
            print(err)
        return json_data


    def write(self, json_data: object) -> None:
        try:
            self.client.write_points(json_data)
        except Exception as err:
            print(err)