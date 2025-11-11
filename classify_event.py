from pathlib import Path
import joblib

from config import MODELS_DIR

MODEL_PATH = MODELS_DIR / "ids_model.pkl"

def classify_event(log_text: str) -> dict:
    """
    Snort 로그를 받아 ML 모델로 공격 유형 예측
    """
    # 학습된 모델이 있다면 로드
    if MODEL_PATH.exists():
        clf = joblib.load(MODEL_PATH)
        # 예시: X_vectorizer.transform([log_text]) 기반으로 예측
        attack_type = clf.predict([log_text])[0]
        confidence = 0.9
    else:
        # 모델 없을 경우 더미 예측
        attack_type = "SQL Injection"
        confidence = 0.91

    return {"attack_type": attack_type, "confidence": confidence}
