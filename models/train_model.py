import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier


def train_kisti_model():
    # 데이터셋 경로 (상대경로)
    dataset_path = os.path.join(os.path.dirname(__file__), "../datasets/trainset.csv")
    model_dir = os.path.join(os.path.dirname(__file__), "../models/saved_models")
    os.makedirs(model_dir, exist_ok=True)

    print(f"[+] 데이터셋 로드 중: {dataset_path}")
    try:
        df = pd.read_csv(dataset_path, encoding="utf-8")
    except Exception as e:
        print(f"[!] 데이터셋 로드 실패: {e}")
        return

    # 열 이름 통일 (대소문자 구분 방지)
    df.columns = [c.strip() for c in df.columns]
    print("[+] 사용 컬럼:", list(df.columns))

    # 공격 유형 열 자동 탐색
    possible_targets = ["attackType", "attack_type", "AttackType"]
    target_col = None
    for col in possible_targets:
        if col in df.columns:
            target_col = col
            break

    if not target_col:
        print("[!] 공격 유형 컬럼을 찾지 못했습니다.")
        return

    # 사용 가능한 피처 자동 필터링
    candidate_features = [
        "sourceIP", "destinationIP", "sourcePort", "destinationPort",
        "protocol", "packetSize", "directionType", "jumboPayloadFlag"
    ]
    features = [col for col in candidate_features if col in df.columns]
    print(f"[+] 사용 가능한 피처: {features}")

    # NaN 처리
    df = df[features + [target_col]].dropna()

    # 문자열 인코딩
    le_dict = {}
    for col in features:
        if df[col].dtype == "object":
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            le_dict[col] = le

    target_le = LabelEncoder()
    df[target_col] = target_le.fit_transform(df[target_col].astype(str))

    X = df[features]
    y = df[target_col]

    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("[+] 랜덤 포레스트 모델 학습 중...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)

    print(f"[+] 학습 완료. 테스트 정확도: {acc:.4f}")

    # 모델 및 인코더 저장
    model_path = os.path.join(model_dir, "kisti_rf_model.pkl")
    joblib.dump(model, model_path)
    joblib.dump(le_dict, os.path.join(model_dir, "feature_encoders.pkl"))
    joblib.dump(target_le, os.path.join(model_dir, "target_encoder.pkl"))

    print(f"[+] 모델 저장 완료: {model_path}")


if __name__ == "__main__":
    train_kisti_model()
