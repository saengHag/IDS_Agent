import joblib
import os

class IDSAgent:
    def __init__(self):
        model_path = r"C:/Users/dlgkr/aisecurity/models/saved_models/kisti_rf_model_retrained.pkl"
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"[!] 학습된 모델을 찾을 수 없습니다: {model_path}")
        print(f"[+] IDS 모델 로드 완료: {model_path}")
        self.model = joblib.load(model_path)

    def process_log(self, log_file):
        # Snort 로그를 구조화한 뒤, ML 모델로 예측
        data = self.parse_snort_log(log_file)
        predictions = self.model.predict(data)
        return {"result": predictions.tolist()}
    
    def parse_snort_log(self, log_file):
        # Snort 로그를 feature vector로 변환하는 로직 작성
        pass
