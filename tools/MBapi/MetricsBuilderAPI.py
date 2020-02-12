from flask import Flask
from flash import request, jsonify
from flask_cors import CORS

from time_sanity_check import sanity_check
from query_db import query_db

app = Flask(__name__)
CORS(app)

app.config['dbconfig'] = {'host': 'localhost',
                          'port': 8086,
                          'database': 'hpcc_monitoring_db',}


@app.route('/api/v1/')
def query_data():
    query_parameters = request.args
    startTime = query_parameters.get('starttime')
    endTime = query_parameters.get('endtime')
    timeInterval = query_parameters.get('interval')
    if sanity_check(startTime, endTime, timeInterval):
        query_db(app.config['dbconfig'], startTime, endTime, timeInterval)
    else:
        return('Quering data failed!')


if __name__ == '__main__':
    app.run(debug=True)