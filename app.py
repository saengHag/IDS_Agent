# 웹 환경 실행하면서 로그 확인. logs_snort에 로그 파일 생성되면 자동으로 분석 진행
from flask import Flask, render_template, jsonify
import threading, os, time
from utils.parser import parse_snort_log
from utils.json_handler import save_json
from utils.logger import log_event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

app = Flask(__name__)

LOG_DIR = "./logs/snort"
OUTPUT_DIR = "./logs/outputs"
RESULT_FILE = os.path.join(OUTPUT_DIR, "auto_analysis.json")


# Snort 로그 감시 핸들러
class SnortLogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".log"):
            log_event(f"[Watcher] Snort 로그 변경 감지: {event.src_path}")
            try:
                with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    if not lines:
                        return
                    latest = lines[-1].strip()
                    parsed = parse_snort_log(latest)
                    save_json(parsed, RESULT_FILE)
                    log_event("[Watcher] 자동 분석 완료 및 JSON 저장됨.")
            except Exception as e:
                log_event(f"[Watcher Error] {e}")


def start_log_listener():
    """별도 스레드에서 Snort 로그 감시 시작"""
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    observer = Observer()
    handler = SnortLogHandler()
    observer.schedule(handler, LOG_DIR, recursive=False)
    observer.start()
    log_event("[Watcher] Snort 로그 감시 스레드 시작됨.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# 🔹 Flask Routes
@app.route("/")
def index():
    """기본 페이지 (대시보드로 리다이렉트 가능)"""
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    """자동 분석 결과를 표시하는 대시보드"""
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            data = f.read()
        return render_template("dashboard.html", data=data)
    else:
        return render_template("dashboard.html", data=None)


@app.route("/get_latest")
def get_latest():
    """AJAX용 — 최신 분석 결과 반환(JSON)"""
    if os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "r", encoding="utf-8") as f:
            return jsonify(eval(f.read()))
    return jsonify({"status": "waiting"})


# Flask 실행 + 감시 스레드 시작
if __name__ == "__main__":
    listener_thread = threading.Thread(target=start_log_listener, daemon=True)
    listener_thread.start()

    log_event("[Flask] IDS-agent 웹 서버 시작됨.")
    app.run(host="127.0.0.1", port=5000, debug=False)
