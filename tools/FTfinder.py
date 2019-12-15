#! /usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import sys
import getopt

from datetime import datetime
from chelper import *

__author__ = "Jie Li"
__copyright__ = "Copyright 2019, Texas Tech University"
__credits__ = ["Jie Li"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Jie Li"
__email__ = "jieli@ttu.edu"
__status__ = "Dev"

def main(argv):
    hostfile = ""
    jobfile = ""
    joboutfile = ""

    try:
        opts, args = getopt.getopt(
            argv, "d:j:vh",
            ["hostDetail=", "jobDetail=", "version", "help"]
        )
    except getopt.GetoptError:
        print("Arguments Error!")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-d", "--hostDetail"):
            hostfile = arg
        elif opt in ("-j", "--jobDetail"):
            jobfile = arg
            joboutfile = jobfile.split(".csv")[0] + "_finish" + ".csv"
        elif opt in ("-v", "--version"):
            print(__version__)
            return 
        elif opt in ("-h", "--help"):
            printFTFHelp()
            return 

    ftime = {}

    try:
        # Get finish time from HostDetail CSV file
        with open(hostfile) as host_csv_file:
            csv_reader = csv.reader(host_csv_file, delimiter=',')
            row0 = next(csv_reader)
            pre_job_list = []
            cur_job_list = []
            for row in csv_reader:
                pre_job_list = cur_job_list
                cur_job_list = []
                for item in row:
                    # item is an array, which contains job ID info
                    if item and item[0] == "[":
                        jobs = item[1:-1].split(", ")
                        cur_job_list.extend(jobs)

                # Compare current job list to previous job list and get the finish time of each job
                for pre_job in pre_job_list:
                    if pre_job not in cur_job_list:
                        ftime.update({
                            pre_job: row[0]
                        })
        # print(ftime)
        # Write finish time to JobDetail CSV file
        with open(jobfile) as job_csv_file:
            with open(joboutfile, "w") as job_csv_out:
                csv_reader = csv.reader(job_csv_file, delimiter=",")
                csv_writer = csv.writer(job_csv_out)

                headers = next(csv_reader)
                headers.append("finishTime")
                csv_writer.writerow(headers)
                for row in csv_reader:
                    jobID = row[0]
                    if jobID in ftime:
                        # print("True")
                        finishtime = ftime[jobID]
                        date = datetime.strptime(finishtime, "%Y-%m-%dT%H:%M:%SZ")
                        date_str = date.strftime("%c")
                        row.append(date_str)
                    csv_writer.writerow(row)
    except:
        print("Error!")
        return

if __name__ == "__main__":
    main(sys.argv[1:])