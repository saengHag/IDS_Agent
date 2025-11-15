import os, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from models.snort_analyzer import analyze_snort_log

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs", "snort")

class SnortLogHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith(".log"):
            print(f"[!] 로그 변경 감지됨: {event.src_path}")
            result_path = analyze_snort_log(event.src_path)
            if result_path:
                self.callback(result_path)

def start_watcher(callback):
    """Snort 로그 디렉토리 감시"""
    os.makedirs(LOG_DIR, exist_ok=True)
    event_handler = SnortLogHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, LOG_DIR, recursive=False)
    observer.start()
    print(f"[*] Snort 로그 감시 시작: {LOG_DIR}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
