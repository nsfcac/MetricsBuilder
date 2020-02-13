# from flask import Flask
# from flask import request, jsonify
# from flask_cors import CORS

import json

from sanity_check import time_sanity_check
from query_db import query_node, query_job_set, query_job_info
from configure import parse_host
from time_stamp import time_stamp
from data_parser import node_data_parser, job_data_parser
from write_csv import build_csv

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
        endTime = '2020-02-12T19:00:00Z'
        timeInterval = '5m'
        node_list = parse_host()
        json_data = {}

        hostfile = "./csv/HostDetail_" + startTime.split("T")[0] + "_" + timeInterval + ".csv"
        jobfile = "./csv/JobDetail_" + startTime.split("T")[0] + "_" + timeInterval + ".csv"
        # node_list = ['10.101.5.5']
        # joblist = ['qu_1122654A30']

        if time_sanity_check(startTime, endTime, timeInterval):

            time_list = time_stamp(startTime, endTime, timeInterval)
            json_data['timeStamp'] = time_list

            node_data = query_node(node_list, config, startTime, endTime, timeInterval)
            pro_node_data = node_data_parser(node_list, node_data, time_list)
            json_data['nodesInfo'] = pro_node_data

            job_list = list(query_job_set(config, startTime, endTime))
            job_info = query_job_info(config, job_list)
            pro_job_data = job_data_parser(job_info)
            json_data['jobsInfo'] = pro_job_data
            
            build_csv(json_data, hostfile, jobfile)
            # print(json.dumps(json_data, indent=2))
        else:
            return('Error: Quering data failed!')
    except Exception as err:
        print(err)

query_data()
# if __name__ == '__main__':
#     # app.run(host='0.0.0.0')