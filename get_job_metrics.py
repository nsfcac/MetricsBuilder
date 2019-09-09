import json
import requests

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    # Get job set
    uge_info, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    if uge_info != None:
        # print(uge_info)
        with open("jobs.json", "wb") as outfile:
            json.dump(uge_info, outfile, indent = 4)
        print("Writing to file succeed")
        jobs_num = len(uge_info)
        print("Jobs numbers: "),
        print(jobs_num)
    else:
        print(err_info)

    # Get Exec Host list
    uge_info, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    if uge_info != None:
        # print(uge_info)
        with open("exechosts.json", "wb") as outfile:
            json.dump(uge_info, outfile, indent = 4)
        print("Writing to file succeed")
        exechosts_num = len(uge_info)
        print("Exec Hosts numbers: "),
        print(exechosts_num)
    else:
        print(err_info)

def get_uge_info(conn_time_out, read_time_out, session, type):

    passwordUrl = "http://129.118.104.35:8182/"
    if type == "jobs":
        url = passwordUrl + type
    elif type == "users":
        url = passwordUrl + type
    elif type == "clusterqueues":
        url = passwordUrl + type
    elif type == "exechosts":
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
