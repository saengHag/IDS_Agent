from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread
from utils.logger import log_event
from models.snort_analyzer import analyze_snort_log
from utils.log_watcher import start_watcher
import os, json

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "logs", "outputs", "report.json")

@app.route("/")
def index():
    """대시보드 페이지"""
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            report_data = json.load(f)
    else:
        report_data = {"attack_type": "None", "confidence": 0, "recommendation": "No events detected."}
    return render_template("dashboard.html", report=report_data)

def notify_clients(report_path):
    """새 분석 결과를 웹 클라이언트에 푸시"""
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        socketio.emit("new_report", report)
        log_event("웹 클라이언트에 새 분석 결과 전송됨")
    except Exception as e:
        log_event(f"결과 전송 오류: {e}")

def start_background_watcher():
    """watchdog 실행 (별도 스레드)"""
    Thread(target=start_watcher, args=(notify_clients,), daemon=True).start()

if __name__ == "__main__":
    log_event("IDS-Agent Flask 서버 시작됨")
    start_background_watcher()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
