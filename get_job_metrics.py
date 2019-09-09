import json
import requests

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

    # Get job list
    job_list, err_info = get_uge_info(conn_time_out, read_time_out, session, "jobs")
    if job_list != None:
        # print(uge_info)
        with open("joblist.json", "wb") as outfile:
            json.dump(job_list, outfile, indent = 4)
        print("Writing file succeed")
    else:
        print(err_info)

    # Get Exec Host list
    exec_hosts, err_info = get_uge_info(conn_time_out, read_time_out, session, "exechosts")
    if exec_hosts != None:
        # print(uge_info)
        with open("exechosts.json", "wb") as outfile:
            json.dump(exec_hosts, outfile, indent = 4)
        print("Writing file succeed")
    else:
        print(err_info)

    # Get Host Summary
    host_summary, err_info = get_uge_info(conn_time_out, read_time_out, session, "hostsummary")
    if host_summary != None:
        # print(uge_info)
        with open("hostsummary.json", "wb") as outfile:
            json.dump(host_summary, outfile, indent = 4)
        print("Writing file succeed")
    else:
        print(err_info)

def get_uge_info(conn_time_out, read_time_out, session, type):

    passwordUrl = "http://129.118.104.35:8182/"
    if type == "jobs":
        url = passwordUrl + type
    elif type == "users":
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
