import datetime, os

LOG_PATH = "./logs/system.log"

def log_event(message: str):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
