import json
import os


def get_queue():
    queue_status = {}
    abs_file_path = os.path.abspath(os.path.dirname(__file__))
    queue_path = os.path.join(abs_file_path, "./shared/queue_status.json")
    with open(queue_path, 'r') as f:
        queue_status = json.load(f)
    return queue_status