import json
from pathlib import Path
from utils.logger import log_event

# ===================================
# JSON 입출력 관리
# ===================================

def save_json(data, path: Path):
    """
    분석 결과나 모델 출력을 JSON 파일로 저장.
    :param data: dict 형식의 데이터
    :param path: 저장할 파일 경로 (Path 객체 권장)
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        log_event(f"JSON 파일 저장 완료: {path.name}")

    except Exception as e:
        log_event(f"JSON 저장 중 오류 발생: {e}")


def load_json(path: Path):
    """
    JSON 파일을 로드하여 dict로 반환.
    :param path: 파일 경로
    :return: dict or None
    """
    try:
        if not path.exists():
            log_event(f"JSON 파일 없음: {path}")
            return None

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log_event(f"JSON 파일 로드 성공: {path.name}")
        return data

    except Exception as e:
        log_event(f"JSON 로드 중 오류 발생: {e}")
        return None
