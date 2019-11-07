#! /usr/bin/python3
import json
import csv

def main():
    with open("./influxdb/2019-04-20T00:00:00Z_2019-04-21T00:00:00Z_5m.json") as json_file:
        with open("./influxdb/1d_5m.csv", "w") as csv_file:

            json_data = json.load(json_file)
            hostDetail = json_data["hostDetail"]
            header_list = []
            host_list = list(hostDetail.keys())
            feature_list = list(hostDetail[host_list[0]].keys())

            csvwriter = csv.writer(csv_file)

            # Write header
            for host in host_list:
                for feature in feature_list:
                    # print(feature, len(hostDetail[host][feature]))
                    header = host + "-" + feature
                    header_list.append(header)   
            
            csvwriter.writerow(header_list)

            # Write value
            timeStamp_len = len(hostDetail[host_list[0]][feature_list[0]]) - 1

            for t in range(timeStamp_len):
                each_row = []
                for host in host_list:
                    for feature in feature_list:
                        if len(hostDetail[host][feature]) != 0:
                            each_row.append(hostDetail[host][feature][t])
                        else:
                            each_row.append(None)
                csvwriter.writerow(each_row)
    print("Done!")

if __name__ == "__main__":
    main()