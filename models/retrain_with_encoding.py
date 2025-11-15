import os
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 models 디렉토리 기준
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "kisti_rf_model.pkl")  # ✅ 실제 파일명 반영
DATA_PATH = os.path.join(BASE_DIR, "../datasets/trainset.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "saved_models", "kisti_rf_model_retrained.pkl")

print(f"[+] 모델 경로: {os.path.abspath(MODEL_PATH)}")
print(f"[+] 데이터 경로: {os.path.abspath(DATA_PATH)}")

# === 기존 모델 로드 ===
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"[!] 모델 파일을 찾을 수 없습니다: {MODEL_PATH}")

print("[+] 기존 모델 불러오는 중...")
model = joblib.load(MODEL_PATH)


print(f"[+] 데이터 로드 중: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

# 학습 속도 향상을 위한 샘플링 (10%)
df = df.sample(frac=0.1, random_state=42)
print(f"[+] 샘플링 완료: {len(df)}행 사용")


target_col = "attackType"
if target_col not in df.columns:
    raise ValueError(f"[!] '{target_col}' 컬럼이 없습니다. CSV 컬럼명을 확인하세요.")

# detectName 인코딩
if "detectName" in df.columns:
    print("[+] detectName 인코딩 중...")
    le_detect = LabelEncoder()
    df["detectName"] = le_detect.fit_transform(df["detectName"].astype(str))
else:
    print("[!] detectName 컬럼이 없어 건너뜁니다.")

# 문자열 컬럼 인코딩
for col in df.columns:
    if df[col].dtype == "object" and col != target_col:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))

X = df.drop(columns=[target_col])
y = df[target_col]

# === 추가 학습 ===
print("[+] 기존 모델에 추가 학습 시도 중...")
try:
    # 기존 모델 파라미터 확장
    if hasattr(model, "n_estimators"):
        model.n_estimators += 100
    model.fit(X, y)
except Exception as e:
    print(f"[!] 기존 모델 업데이트 불가 → 새 모델로 대체: {e}")
    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X, y)

# === 저장 ===
joblib.dump(model, OUTPUT_PATH)
print(f"[✓] 재학습 완료! 새 모델 저장됨 → {os.path.abspath(OUTPUT_PATH)}")
