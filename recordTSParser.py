import json

with open("./pyplot/recordTS.json") as json_file:
    data = json.load(json_file)
    time_stamp = []
    power_val = []
    job_num = []
    job_set = []
    sorted_data = []

    for item in data:
        time_stamp.append(item['TimeStamp'])
        total_power = 0
        for job in item['JobList']:
            total_power += job['Power']
            if job['JobId'] not in job_set:
                job_set.append(job['JobId'])
        power_val.append(round(total_power, 2))
        job_num.append(len(item['JobList']))
    job_set.sort()

    for index, jobid in enumerate(job_set):
        sorted_data.append({"JobId": jobid, "ExecCores": [], "Power": []})
        for item in data:
            exec_cores = None
            power = None
            for job in item['JobList']:
                if jobid == job['JobId']:
                    exec_cores = job['ExecCores']
                    power = job['Power']
            sorted_data[index]['ExecCores'].append(exec_cores)
            sorted_data[index]['Power'].append(power)

# print(f"Time Stamp: {time_stamp}")
# print(f"Job List: {job_set}")
# print(f"Total Power: {power_val}")
# print(f"Total Running Jobs: {job_num}")
# print(f"Job details: {sorted_data[111]}")

# print(f"Jobs Length: {len(job_set)}")
# print(f"Dataset Length: {len(sorted_data)}")
#
# with open("./pyplot/dataset.json", "w") as dataset:
#     json.dump(sorted_data, dataset, indent = 4, sort_keys = True)
#
# with open("./pyplot/timestamp.json", "w") as timestamp:
#     json.dump(time_stamp, timestamp, indent = 4, sort_keys = True)
#
# with open("./pyplot/totalpower.json", "w") as totalpower:
#     json.dump(power_val, totalpower, indent = 4, sort_keys = True)
