import json
import requests

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    ## Dump file
    # job_info_list, err_info_list = get_hpcjob_data(conn_time_out, read_time_out, session)
    #
    # if job_info_list != None:
    #     # print(job_info_list)
    #     with open("hpcjobs.json", "wb") as outfile:
    #         json.dump(job_info_list, outfile, indent = 4)
    #     print("Writing to file succeed")
    # else:
    #     print(err_info_list)

    # Get job list
    uge_info, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    if uge_info != None:
        # print(uge_info)
        jobs_num = len(uge_info)
        print("Jobs numbers: "),
        print(jobs_num)
    else:
        print(err_info)

    # Get user list
    uge_info, err_info = get_uge_info(conn_time_out, read_time_out, session, "users")
    if uge_info != None:
        # print(uge_info)
        projects_num = len(uge_info)
        print("Users numbers: "),
        print(projects_num)
    else:
        print(err_info)

    # Get host summary list
    uge_info, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")
    if uge_info != None:
        # print(uge_info)
        hostsummary_num = len(uge_info)
        print("Host summary numbers: "),
        print(hostsummary_num)
    else:
        print(err_info)

def get_uge_info(conn_time_out, read_time_out, session, type):

    passwordUrl = "http://129.118.104.35:8182/"
    if type == "jobs":
        url = passwordUrl + type
    elif type == "users":
        url = passwordUrl + type
    elif type == "hostsummary":
        url = passwordUrl + "hostsummary/1/500"
    else:
        return None, "UGE API ERROR"

    try:
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))
        response.raise_for_status()
        data = response.json()
        return data, str(None)

    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

if __name__ == "__main__":
    main()
