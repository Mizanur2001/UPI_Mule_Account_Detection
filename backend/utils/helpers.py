from datetime import datetime

def parse_time(ts):
    return datetime.fromisoformat(ts)

def now():
    return datetime.now()
