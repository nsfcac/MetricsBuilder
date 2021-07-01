import yaml
import pandas as pd


def init_tsdb_connection(config_tsdb: dict) -> str:
    """
    Generate TimeScaleDB connection
    """
    db_host = config_tsdb['host']
    db_port = config_tsdb['port']
    db_user = config_tsdb['user']
    db_pswd = config_tsdb['password']
    db_dbnm = config_tsdb['database']
    connection = f"postgresql://{db_user}:{db_pswd}@{db_host}:{db_port}/{db_dbnm}"
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


def gene_node_id_mapping(con: object) -> dict:
    """
    Generate nodename-id mapping dict
    """
    mapping_sql = "SELECT nodeid, hostname FROM nodes;"
    mapping_df = pd.read_sql_query(mapping_sql,con=con)
    mapping = pd.Series(mapping_df.hostname.values, index=mapping_df.nodeid).to_dict()
    return mapping