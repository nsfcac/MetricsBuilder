import json
import time
import datetime
import requests
import warnings
from collections import Counter
from threading import Thread
from threading import Timer
from time import sleep

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():

    with open("./records/records_10mins.json") as record_file:
        data = json.load(record_file)
        aggregate(timestep, data)

def aggregate(timestep, data):
    timeRange = [data[0]['timeStamp'], data[-1]['timeStamp']]
    timeSteps = timestep

if __name__ == "__main__":
    main()
