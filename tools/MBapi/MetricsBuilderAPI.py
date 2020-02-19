from flask import Flask
from flask import request
from flask_cors import CORS

import json

from sanity_check import time_sanity_check
from query_db import query_node_info, query_job_list, query_job_info
from configure import parse_host
from time_stamp import time_stamp
from process_data import process_node_data, process_job_data
# from write_csv import build_csv

app = Flask(__name__)
CORS(app)
config = {'host': 'localhost',
          'port': 8086,
          'database': 'hpcc_monitoring_db',}


@app.route('/api/v1/')
def query_data() -> str:
    try:
        query_parameters = request.args

        start = query_parameters.get('starttime')
        end = query_parameters.get('endtime')
        timeInterval = query_parameters.get('interval')
        value = "max"
        # start = '2020-02-12T14:00:00Z'
        # end = '2020-02-12T19:00:00Z'
        # timeInterval = '5m'
        node_list = parse_host()
        json_data = {}

        # hostfile = "./csv/HostDetail_" + start + "_" + end + "_" + timeInterval + ".csv"
        # jobfile = "./csv/JobDetail_" + start + "_" + end + "_"  + timeInterval + ".csv"
        # node_list = ['10.101.5.5']
        # joblist = ['qu_1122654A30']

        if time_sanity_check(start, end, timeInterval):

            print("Getting Time Stamp...")
            time_list = time_stamp(start, end, timeInterval)
            json_data['timeStamp'] = time_list

            print("Getting Nodes Information...")
            node_data = query_node_info(node_list, config, start, end, timeInterval, value)
            pro_node_data = process_node_data(node_list, node_data, time_list, value)
            json_data['nodesInfo'] = pro_node_data

            print("Getting Jobs Information...")
            job_list = query_job_list(config, start, end)
            job_data = query_job_info(config, job_list)
            pro_job_data = process_job_data(job_data)
            json_data['jobsInfo'] = pro_job_data
            
            # print("Writting to csv files...")
            print("Sending data...")
            # build_csv(json_data, hostfile, jobfile)
            return(json.dumps(json_data))
            # print(json.dumps(json_data, indent=2))
        else:
            return('Error: Quering data failed!')
    except Exception as err:
        print(err)


query_data()


if __name__ == '__main__':
    app.run(host='0.0.0.0')