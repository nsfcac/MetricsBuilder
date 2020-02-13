from flask import Flask
from flask import request
from flask_cors import CORS

import requests

app = Flask(__name__)
CORS(app)

@app.route('/api/v1/')
def send_req() -> str:

    startTime = request.args["starttime"]
    endTime = request.args["endtime"]
    interval = request.args["interval"]

    url = "http://10.10.1.4:5000/api/v1/?starttime=" + startTime + "&endtime=" + endTime + "&interval=" + interval

    res = requests.get(url)

    return res

if __name__ == '__main__':
    app.run(host='0.0.0.0')