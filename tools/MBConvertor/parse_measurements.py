import re
from DBcm import QueryInfluxdb

def parse_measurement(client: object) -> dict:
    measurements = client.list_measurements()

    job_measurements = []
    sys_measurements = []
    for mea in measurements:
        if bool(re.search(r'\d', mea["name"])):
            job_measurements.append(mea["name"])
        else:
            sys_measurements.append(mea["name"])

    result = {
        "job_measurements": job_measurements,
        "sys_measurements": sys_measurements
    }
    return result
