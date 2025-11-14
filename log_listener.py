# snort 로그 자동 감시. snort 폴더 내에 파일 생성되면 watchdog으로 탐지함
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from agent_core import AgentCore
from utils.logger import log_event
from utils.json_handler import save_json
import os

LOG_DIR = "./logs/snort"
OUTPUT_DIR = "./logs/outputs"

class SnortLogHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.agent = AgentCore()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".log"):
            log_event(f"Snort 로그 변경 감지: {event.src_path}")
            with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if lines:
                    # 가장 최근 로그 1줄만 분석 (필요시 다중 처리 가능)
                    latest = lines[-1]
                    result = self.agent.process_log(latest)
                    os.makedirs(OUTPUT_DIR, exist_ok=True)
                    save_json(result, os.path.join(OUTPUT_DIR, "auto_analysis.json"))
                    log_event("자동 분석 완료 및 저장됨.")

def start_listener():
    os.makedirs(LOG_DIR, exist_ok=True)
    observer = Observer()
    handler = SnortLogHandler()
    observer.schedule(handler, path=LOG_DIR, recursive=False)
    observer.start()
    log_event("Snort 로그 자동 감시 시작됨.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_listener()
