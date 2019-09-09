import json

def main():
    with open('hpcjobs.json') as json_file:
        hosts = json.load(json_file)

    print(f"Total jobs: {len(hosts)}")

    for host in hosts:

        # host name
        print(f"hostname: {host['hostname'].split('.')[0]}")
        hostip = get_hostip(host['hostname'].split('.')[0])
        # host ip
        print(f"host IP: {hostip}")

        # cpu average usage
        if host['resourceNumericValues'].get('np_load_avg') != None:
            print(f"CPU usage: {host['resourceNumericValues']['np_load_avg']}")
        # memory usage
        if host['resourceNumericValues'].get('m_mem_total') != None:
            print(f"Memory usage: {host['resourceNumericValues']['m_mem_free']}")

        for job in host['jobList']:
            if (job['masterQueue'] == "MASTER"):
                continue
            jobID = job['id']

            if 'taskId' in job:
                jobID = jobID + "-" + job['taskId']

def get_hostip(hostname):
    if '-' in hostname:
        n, h2, h1 = hostname.split('-')
        return '10.101.' + h2 + "." + h1
    return None

if __name__=="__main__":
    main()
