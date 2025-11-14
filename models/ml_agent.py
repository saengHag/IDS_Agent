class MLAgent:
    def __init__(self, model_path="./models/model.pkl"):
        self.model_path = model_path
        self.model = None  # 나중에 joblib/pickle 로드

    def predict(self, parsed_data: dict) -> dict:
        # Snort 로그에서 피처 추출 후 예측 로직 작성
        return {
            "attack_type": "Port Scan",
            "confidence": 0.92,
            "raw_features": parsed_data
        }
