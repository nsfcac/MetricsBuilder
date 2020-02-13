import csv
import json
import getopt
import sys

def main(argv):
    json_file_name = ""

    try:
        opts, args = getopt.getopt(
            argv, "f:",
            ["jsonfile="]
        )
    except getopt.GetoptError:
        print("Arguments Error!")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-f", "--jsonfile"):
            json_file_name = arg
        else:
            print("Error")
            return

    try:
        with open(json_file_name, "r") as json_file:
            json_data = json.load(json_file)
    except Exception as err:
        print(err)
        return

    hostfile = "./csv/HostDetail_" + json_file_name.split(".")[0] + ".csv"
    jobfile = "./csv/JobDetail_" + json_file_name.split(".")[0] + ".csv"

    build_csv(json_data, hostfile, jobfile)
    return


def build_csv(json_data: dict, hostfile: str, jobfile: str) -> None:
    """Convert json files to CSV files"""
    
    hostDetail = json_data["nodesInfo"]
    jobDetail = json_data["jobsInfo"]
    time_List = json_data["timeStamp"]

    print("Time Stamp length: ", len(time_List))

    # Write host details into a CSV file
    with open(hostfile, "w") as host_csv_file:
        header_list = ["TimeStamp"]
        host_list = list(hostDetail.keys())
        # print("nodes length: ", len(host_list))
        feature_list = list(hostDetail[host_list[0]].keys())
        # print("features length: ", len(feature_list))
        csvwriter = csv.writer(host_csv_file)

        for feature in feature_list:
            print(feature, len(hostDetail[host_list[455]][feature]))
        
        # Write header
        for host in host_list:
            for feature in feature_list:
                header = host + "-" + feature
                header_list.append(header)   
        
        print("header length: ", len(header_list))
        csvwriter.writerow(header_list)

        # Write value
        for i, timestamp in enumerate(time_List):
            each_row = [timestamp]
            for host in host_list:
                for feature in feature_list:
                    each_row.append(hostDetail[host][feature][i])
            csvwriter.writerow(each_row)
    
    # Write job details into a CSV file
    with open(jobfile, "w") as job_csv_file:
        header_list = ["JobID"]
        job_list = list(jobDetail.keys())
        feature_list = list(jobDetail[job_list[0]].keys())

        csvwriter = csv.writer(job_csv_file)
        # Write header
        for feature in feature_list:
            header_list.append(feature)
        
        csvwriter.writerow(header_list)

        # Write value
        for job in job_list:
            each_row = [job]
            for feature in feature_list:
                each_row.append(jobDetail[job][feature])
            csvwriter.writerow(each_row)


if __name__ == "__main__":
    main(sys.argv[1:])