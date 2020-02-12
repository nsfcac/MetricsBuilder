from influxdb import InfluxDBClient

class QueryInfluxdb():

    def __init__(self, config: dict) -> None:
        self.configuration = config
    
    def get(self, sql: str) -> list:
        json_data = {}
        try:
            client = InfluxDBClient(**self.configuration)
            influxdbQuery = client.query(sql)
            json_data['data'] = list(influxdbQuery.get_points())
        except Exception as err:
            error = {
                'title': 'Query InfluxDB Exception',
                'meta': {'args': err.args}
            }
            json_data['errors'] = [error]
            print("Error: " + self.__str__() + " : " + err.message)
        return json_data