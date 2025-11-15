import os
import re
import json
from datetime import datetime
import joblib
import pandas as pd
from utils.logger import log_event
from utils.json_handler import save_json

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
LOG_DIR = os.path.join(PROJECT_DIR, "logs", "snort")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "logs", "outputs")
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "kisti_model.pkl")

# === Snort 로그 파일 패턴 ===
LOG_PATTERN = re.compile(
    r"\[\*\*\]\s+\[\d+:(\d+):\d+\]\s+(.*?)\s+\[\*\*\]\s+"
    r"\[Priority:\s*(\d+)\]\s+\{(\w+)\}\s+([\d\.]+)\s*->\s*([\d\.]+)"
)


def parse_snort_log(file_path):
    """Snort 로그를 구조화된 리스트로 변환"""
    events = []
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            matches = LOG_PATTERN.findall(content)
            for match in matches:
                sid, msg, priority, proto, src, dst = match
                events.append({
                    "sid": int(sid),
                    "message": msg.strip(),
                    "priority": int(priority),
                    "protocol": proto.strip(),
                    "source": src.strip(),
                    "destination": dst.strip()
                })
    except Exception as e:
        print(f"[!] 로그 파싱 중 오류 발생: {e}")
    return events


def analyze_snort_log(log_path=None):
    """
    Snort 로그를 분석하고 결과를 JSON으로 저장 후 경로를 반환.
    - log_path 지정 시 해당 파일 분석
    - 미지정 시 logs/snort 내 최신 로그 분석
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1️⃣ 분석 대상 로그 결정
    if log_path and os.path.exists(log_path):
        target_log = log_path
    else:
        log_files = sorted(
            [f for f in os.listdir(LOG_DIR) if f.endswith(".log")],
            key=lambda x: os.path.getmtime(os.path.join(LOG_DIR, x)),
            reverse=True
        )
        if not log_files:
            print("[!] Snort 로그 파일이 없습니다.")
            return None
        target_log = os.path.join(LOG_DIR, log_files[0])

    print(f"[*] Snort 로그 분석 중: {target_log}")
    log_event(f"Snort 로그 감지됨: {target_log}")

    # 2️⃣ 로그 파싱
    events = parse_snort_log(target_log)
    if not events:
        print("[!] 파싱된 이벤트가 없습니다.")
        return None

    df = pd.DataFrame(events)
    print(f"[+] {len(df)}개의 이벤트 파싱 완료")

    # 3️⃣ 모델 로드
    if not os.path.exists(MODEL_PATH):
        print(f"[!] 모델 파일을 찾을 수 없습니다: {MODEL_PATH}")
        return None

    try:
        model = joblib.load(MODEL_PATH)
        print(f"[+] ML 모델 로드 완료: {MODEL_PATH}")
    except Exception as e:
        print(f"[!] 모델 로드 실패: {e}")
        return None

    # 4️⃣ 특징 벡터화
    df["priority"] = df["priority"].astype(int)
    df["proto_code"] = df["protocol"].astype("category").cat.codes
    feature_cols = ["priority", "proto_code"]
    X = df[feature_cols]

    # 5️⃣ 예측 수행
    try:
        predictions = model.predict(X)
        df["prediction"] = predictions
        print(f"[+] {len(predictions)}개의 이벤트 예측 완료")
    except Exception as e:
        print(f"[!] 예측 중 오류 발생: {e}")
        df["prediction"] = "unknown"

    # 6️⃣ 결과 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"snort_analysis_{timestamp}.json")

    save_json(df.to_dict(orient="records"), output_file)
    log_event("Snort 분석 완료", f"{len(df)}개의 이벤트 분석 후 결과 저장")
    print(f"[✓] 분석 결과 저장 완료: {output_file}")

    return output_file


if __name__ == "__main__":
    analyze_snort_log()
