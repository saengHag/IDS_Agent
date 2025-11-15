from datetime import datetime
from pathlib import Path

# 로그 디렉토리 및 파일 경로 설정
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "system.log"

# 로그 기록 함수
def log_event(message: str, console: bool = True):
    """
    :param message: 로그에 기록할 메시지
    :param console: 콘솔 출력 여부 (기본 True)
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        # 파일에 기록
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

        # 콘솔에도 출력
        if console:
            print(log_entry)

    except Exception as e:
        print(f"[LOGGER ERROR] 로그 기록 중 오류 발생: {e}")
