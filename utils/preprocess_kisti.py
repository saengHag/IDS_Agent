import pandas as pd
import os

def preprocess_kisti_dataset(
    input_path=r"C:/Users/dlgkr/Downloads/training_set.csv",
    output_path="../datasets/trainset.csv",
    chunk_size=100000
):
    """
    KISTI 네트워크 침입탐지 데이터셋 전처리 (스트리밍 버전)
    - 메모리 절약: chunk_size 단위로 읽기
    - 구분자 자동 감지
    - 결측치/중복 제거
    """

    print(f"[+] KISTI 데이터셋 로드 중: {input_path}")

    # --- 1. 구분자 감지 ---
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        sample = f.read(2000)
    delimiter = "," if sample.count(",") > sample.count("\t") else "\t"
    print(f"[+] 구분자 감지됨: '{delimiter}'")

    # --- 2. 출력 경로 생성 ---
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        os.remove(output_path)

    # --- 3. 스트리밍 방식으로 읽기 ---
    total_rows = 0
    chunk_idx = 0

    try:
        for chunk in pd.read_csv(
            input_path,
            sep=delimiter,
            engine="c",
            chunksize=chunk_size,
            encoding="utf-8",
            on_bad_lines="skip"
        ):
            chunk = chunk.dropna()
            chunk = chunk.drop_duplicates()
            chunk.to_csv(output_path, mode="a", index=False, header=(chunk_idx == 0))
            total_rows += len(chunk)
            chunk_idx += 1
            print(f"  [✔] {chunk_idx}번째 청크 완료 — 누적 {total_rows:,}행")
    except Exception as e:
        print(f"[!] 처리 중 오류 발생: {e}")
        return

    print(f"[+] 전처리 완료: {os.path.abspath(output_path)}")
    print(f"[+] 총 처리된 행 수: {total_rows:,}행")


if __name__ == "__main__":
    preprocess_kisti_dataset()
