from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

import json

from sanity_check import time_sanity_check
from query_db import query_node, query_job_set, query_job_info

# app = Flask(__name__)
# CORS(app)
config = {'host': 'localhost',
          'port': 8086,
          'database': 'hpcc_monitoring_db',}


# @app.route('/api/v1/')
def query_data() -> str:
    try:
        # query_parameters = request.args
        # startTime = query_parameters.get('starttime')
        # endTime = query_parameters.get('endtime')
        # timeInterval = query_parameters.get('interval')
        startTime = '2020-02-12T14:00:00Z'
        endTime = '2020-02-12T14:30:00Z'
        timeInterval = '5m'
        node = ['10.101.6.11']
        # joblist = ['qu_1122654A30']

        if time_sanity_check(startTime, endTime, timeInterval):
            # node_data = query_node(node, config, startTime, endTime, timeInterval)
            job_set = query_job_set(config, startTime, endTime)
            job_list = list(job_set)
            job_info = query_job_info(config, job_list)
            print(json.dumps(job_info, indent=2))
        else:
            return('Error: Quering data failed!')
    except Exception as err:
        print(err)

query_data()
# if __name__ == '__main__':
#     # app.run(host='0.0.0.0')