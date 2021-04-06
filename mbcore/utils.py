import yaml


def init_tsdb_connection(config_tsdb: dict) -> str:
    """
    Generate TimeScaleDB connection
    """
    db_host = config_tsdb['host']
    db_port = config_tsdb['port']
    db_user = config_tsdb['user']
    db_pswd = config_tsdb['password']
    db_dbnm = config_tsdb['database']
    connection = f"postgres://{db_user}:{db_pswd}@{db_host}:{db_port}/{db_dbnm}"
    return connection


def init_tsdb_dsn(config_tsdb: dict) -> str:
    """
    Generate Aiopy dsn
    """
    host = config_tsdb['host']
    port = config_tsdb['port']
    user = config_tsdb['user']
    password = config_tsdb['password']
    dbname = config_tsdb['database']
    dsn = f"dbname={dbname} user={user} password={password} host={host} port={port}"
    return dsn


def parse_config(path: str) -> dict:
    """
    Read configuration file
    """
    cfg = {}
    try:
        with open(path, 'r') as ymlfile:
            cfg = yaml.safe_load(ymlfile)
        return cfg
    except Exception as err:
        print(err)


def gene_host_id_mapping(conn: object) -> dict:
    """
    Generate hostname-id mapping dict
    """
    mapping = {}
    cur = conn.cursor()
    query = "SELECT nodeid, hostname FROM nodes"
    cur.execute(query)
    for (nodeid, hostname) in cur.fetchall():
        mapping.update({
            hostname: nodeid
        })
    cur.close()
    return mapping