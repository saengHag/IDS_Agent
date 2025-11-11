# log_listener.py
import time, json, requests
from pathlib import Path
from config import SNORT_LOG_PATH

API_URL = "http://127.0.0.1:5000/analyze"
LAST_POS_FILE = Path("logs/last_pos.txt")

def read_new_lines(file_path: Path, last_pos: int):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(last_pos)
        new_data = f.read()
        new_pos = f.tell()
    return new_data, new_pos

def main():
    SNORT_LOG_PATH.parent.mkdir(exist_ok=True)
    if not SNORT_LOG_PATH.exists():
        print("[WAIT] Snort 로그 파일을 기다리는 중...")
        while not SNORT_LOG_PATH.exists():
            time.sleep(2)

    last_pos = 0
    if LAST_POS_FILE.exists():
        last_pos = int(LAST_POS_FILE.read_text())

    print(f"[START] Snort 로그 감시 시작: {SNORT_LOG_PATH}")

    while True:
        new_data, new_pos = read_new_lines(SNORT_LOG_PATH, last_pos)
        if new_data.strip():
            for line in new_data.strip().splitlines():
                try:
                    payload = {"event": line}
                    requests.post(API_URL, json=payload, timeout=10)
                    print(f"[+] 신규 이벤트 전송 완료: {line[:80]}...")
                except Exception as e:
                    print(f"[!] 전송 실패: {e}")
        last_pos = new_pos
        LAST_POS_FILE.write_text(str(last_pos))
        time.sleep(2)

if __name__ == "__main__":
    main()
