from datetime import datetime

def get_phase_time(client: object) -> int:
    """
    Get first time stamp of each measurement
    """
    phase_time = []

    try:            
        phase1_start_sql = "SELECT first(error) FROM CPU_Temperature WHERE host='10.101.1.1'"
        phase2_start_sql = "SELECT first(cpuusage) FROM cluster_unified_metrics WHERE host='10.101.1.1'"

        phase1_start = client.get(phase1_start_sql)[0]["time"]
        phase_time.append(phase1_start)

        phase2_start = client.get(phase2_start_sql)[0]["time"]
        phase_time.append(phase2_start)

    except Exception as err:
        print(err)
    
    return phase_time

# fst_mea = ["CPU_Temperature", "Inlet_Temperature", "CPU_Usage", 
#             "Memory_Usage", "Fan_Speed", "Node_Power_Usage"]
# sec_mea = ["cluster_unified_metrics", "Current_Jobs_ID"]

def 