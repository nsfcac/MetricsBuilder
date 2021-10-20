def process_idrac9_df(metric: str, idrac9_df: object, mapping: dict) -> dict:
    """
    Process idrac9 metrics dataframe
    """
    nodes_info = {}
    grouped_df = idrac9_df.groupby(['nodeid', 'label'])
    for key, item in grouped_df:
        node_name = mapping[key[0]]
        metric_name = f'{metric}-{key[1]}'
        metric_value = grouped_df.get_group(key)['value'].tolist()
        if node_name not in nodes_info:
            nodes_info.update({
                node_name: {
                    metric_name: metric_value
                }
            })
        else:
            nodes_info[node_name].update({
                metric_name: metric_value
            })
    return nodes_info


def process_slurm_df(metric: str, df: object, mapping: dict) -> dict:
    """
    Process idrac9 metrics dataframe
    """
    nodes_info = {}
    grouped_df = df.groupby(['nodeid'])
    for key, item in grouped_df:
        node_name = mapping[key]
        metric_name = metric
        metric_value = grouped_df.get_group(key)['value'].tolist()
        if node_name not in nodes_info:
            nodes_info.update({
                node_name: {
                    metric_name: metric_value
                }
            })
        else:
            nodes_info[node_name].update({
                metric_name: metric_value
            })
    return nodes_info


def process_node_jobs_df(node_jobs_df:object, mapping: dict) -> dict:
    """
    Process node_jobs dataframe which is get from node_jobs table in TSDB.
    """
    node_jobs = {}
    try:
        node_jobs_df['time'] = node_jobs_df['time'].apply(
            lambda x: int(x.timestamp())
        )
        node_jobs_df['fl_jobs'] = node_jobs_df.apply(
            lambda df_row: flatten_array(df_row, 'jobs'), axis = 1)
        node_jobs_df['fl_cpus'] = node_jobs_df.apply(
            lambda df_row: flatten_array(df_row, 'cpus'), axis = 1)
        node_jobs_df.drop(columns = ['jobs', 'cpus'], 
                        inplace = True)
        node_jobs_df.rename(columns={'fl_jobs': 'jobs', 'fl_cpus': 'cpus'}, 
                        inplace = True)

        grouped_df = node_jobs_df.groupby(['nodeid'])#[['time', 'jobs', 'cpus']]
        for key, item in grouped_df:
            jobs = grouped_df.get_group(key)['jobs'].tolist()
            cpus = grouped_df.get_group(key)['cpus'].tolist()
            node_name = mapping[key]
            node_jobs.update({
                node_name:{
                    'jobs': jobs,
                    'cpus': cpus
                }
            })
    except Exception as err:
        pass
    return node_jobs


def flatten_array(df_row, column: str):
    jobs = []
    cpus = []
    job_id_array = df_row['jobs']
    cpus_array = df_row['cpus']
    try:
        if job_id_array:
            # Flatten array
            fl_job_id_array = [item for sublist in job_id_array for item in sublist]
            fl_cpus_array = [item for sublist in cpus_array for item in sublist]

            # Only keep unique jobs
            for i, job in enumerate(fl_job_id_array):
                if job not in jobs:
                    jobs.append(job)
                    cpus.append(fl_cpus_array[i])
    except:
        # print(f"{df_row['time']} - {df_row['nodeid']}")
        pass
    if column == 'jobs':
        return jobs
    else:
        return cpus