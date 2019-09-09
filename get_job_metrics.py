import json
import requests

def main():
    conn_time_out = 15
    read_time_out = 40

    session = requests.Session()

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
    job_list, err_info = get_job_list(conn_time_out, read_time_out, session)
    if job_list != None:
        # print(job_list)
        jobs_num = len(job_list)
        print("Jobs numbers: "),
        print(jobs_num)
    else:
        print(err_info)

    # Get project list
    project_list, err_info = get_project_list(conn_time_out, read_time_out, session)
    if project_list != None:
        print(project_list)
        projects_num = len(project_list)
        print("Projects numbers: "),
        print(projects_num)
    else:
        print(err_info)

    # Get user list
    user_list, err_info = get_user_list(conn_time_out, read_time_out, session)
    if user_list != None:
        print(user_list)
        users_num = len(user_list)
        print("Users numbers: "),
        print(users_num)
    else:
        print(err_info)


def get_job_list(conn_time_out, read_time_out, session):
    try:
        url = "http://129.118.104.35:8182/jobs"
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))

        response.raise_for_status()
        data = response.json()

        return data, str(None)
    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

def get_project_list(conn_time_out, read_time_out, session):
    try:
        url = "http://129.118.104.35:8182/projects"
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))

        response.raise_for_status()
        data = response.json()

        return data, str(None)
    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

def get_user_list(conn_time_out, read_time_out, session):
    try:
        url = "http://129.118.104.35:8182/users"
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))

        response.raise_for_status()
        data = response.json()

        return data, str(None)
    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

def get_hpcjob_data(conn_time_out, read_time_out, session):
    try:
        url = "http://129.118.104.35:8182/hostsummary/1/500"
        response = session.get(url, verify = False, timeout = (conn_time_out, read_time_out))

        response.raise_for_status()
        data = response.json()

        return data, str(None)
    except requests.exceptions.RequestException as e:
        print("Request Error")
        return None, str(e)

if __name__ == "__main__":
    main()
