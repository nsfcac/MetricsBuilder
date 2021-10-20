import io
import json
import pytz
import hostlist
import subprocess
import pandas as pd
from datetime import datetime, timezone

DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

attributes_map = {
    'job_id': 'JobIDRaw', 
    'array_job_id': 'JobID', # jobID = ArrayJobID_ArrayTaskID
    'array_task_id': 'NaN', #jobID = ArrayJobID_ArrayTaskID
    'name': 'JobName',
    'job_state': 'State', 
    'user_id': 'UID', 
    'user_name': 'User',
    'group_id': 'GID',
    'cluster': 'Cluster', 
    'partition': 'Partition', 
    'command': 'NaN', 
    'current_working_directory': 'WorkDir', 
    'batch_flag': 'NaN', 
    'batch_host': 'NaN',
    'nodes': 'NodeList', 
    'node_count': 'NNodes',
    'cpus': 'NCPUS',
    'tasks': 'NaN', # ? cpus,
    'tasks_per_node': 'NaN', 
    'cpus_per_task': 'NaN', 
    'memory_per_node': 'NaN', 
    'memory_per_cpu': 'ReqMem',
    'priority': 'Priority',
    'time_limit': 'TimelimitRaw',
    'deadline': 'NaN', 
    'submit_time': 'Submit',
    'preempt_time':'NaN',
    'suspend_time': 'Suspended', 
    'eligible_time': 'Eligible',
    'start_time': 'Start',
    'end_time': 'End',
    'resize_time': 'NaN', 
    'restart_cnt': 'NaN',
    'exit_code': 'ExitCode',
    'derived_exit_code': 'DerivedExitCode'}


def fetch_job_data(starttime: str, endtime: str):

    attributes = [ j for i, j in attributes_map.items() if j!= 'NaN' ]

    # df = get_jobs_acct_df(jobids, attributes)
    df = get_jobs_acct_df(starttime, endtime, attributes)

    if not df.empty:
        df = process_jobs_acct_df(df)
        df = df.set_index('job_id')

        # Conver to json
        result = df.to_json(orient='index')
        parsed = json.loads(result)

        return parsed


def get_jobs_acct_df(starttime: str, endtime: str, attributes: list):
    command = [
        "ssh username@login.hpcc.ttu.edu " \
        + "'sacct --starttime " + starttime \
        + " --endtime " + endtime \
        + " --format=all --parsable2 --allusers --partition nocona --state COMPLETED,RUNNING'"
    ]

    # print(command)
    rtn_str = subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

    if rtn_str:
        # io.StringIO, in-memory-file-like object
        df_raw = pd.read_csv(io.StringIO(rtn_str), sep='|')
        # Remove Unnamed columns
        df_raw = df_raw.loc[:, ~df_raw.columns.str.contains('^Unnamed')]
        df_reduced = df_raw[attributes]
        return df_reduced


def process_jobs_acct_df(df):
    # Generate a rename map
    rename_map = {}
    for i, j in attributes_map.items():
        if j!= 'NaN':
            rename_map.update({
                j: i
            })
    # Remove batch and entern info
    df = df[(df['JobName'] != 'batch') & (df['JobName'] != 'extern')]

    # Remove job step (which contains . in JobIDRaw)
    df = df[~df['JobIDRaw'].str.contains('\.')]

    # Derive array job id and task id
    df['array_job_id'] = df['JobID'].apply(lambda x: x.split('_')[0] if '_' in x else 0)
    df['array_task_id'] = df['JobID'].apply(lambda x: x.split('_')[1] if '_' in x else 0)
    
    # The job_id will replaced by JobIDRaw, therefore drop 'JobID
    df = df.drop(columns=['JobID'])
    df = df.rename(columns=rename_map)
    df['job_id'] = df['job_id'].astype(int)
    df['array_job_id'] = df['array_job_id'].astype(int)
    # Cannot handle task_id like [150-196]
    # df['array_task_id'] = df['array_task_id'].astype(int)
    df['user_id'] = df['user_id'].astype(int)
    df['group_id'] = df['group_id'].astype(int)
    df['priority'] = df['priority'].astype(int)
    df['time_limit'] = df['time_limit'].astype(int)

    df['eligible_time'] = df['eligible_time'].apply(lambda x: convert_to_epoch(x))
    df['submit_time'] = df['submit_time'].apply(lambda x: convert_to_epoch(x))
    df['start_time'] = df['start_time'].apply(lambda x: convert_to_epoch(x))
    df['end_time'] = df['end_time'].apply(lambda x: convert_to_epoch(x))

    df['nodes'] = df['nodes'].apply(lambda x: hostlist.expand_hostlist(x))

    # Todo: Add swap info
    df.reset_index(drop=True, inplace=True)
    
    return df


def convert_to_epoch(time_str: str):
    try:
        central = pytz.timezone('US/Central')
        time_t = datetime.strptime(time_str, DATETIME_FORMAT)
        time_tz = central.localize(time_t)
        time_epoch = int(time_tz.timestamp())
    except:
        time_epoch = 0
    return time_epoch