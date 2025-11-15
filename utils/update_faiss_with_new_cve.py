import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from openai import OpenAI

# === 기본 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)

DATA_DIR = os.path.join(PROJECT_DIR, "datasets")
NEW_CVE_DIR = os.path.join(DATA_DIR, "new-cve")  # 새로 추가된 CVE 폴더

VECTOR_DIR = os.path.join(PROJECT_DIR, "models", "vectorstore")
INDEX_PATH = os.path.join(VECTOR_DIR, "threat_knowledge.index")
META_PATH = os.path.join(VECTOR_DIR, "threat_knowledge_meta.json")

# === OpenAI API 키 설정 ===
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === 함수: 새 CVE 파일 로드 ===
def load_new_cve_entries():
    entries = []
    if not os.path.exists(NEW_CVE_DIR):
        print(f"[!] 새 CVE 폴더가 없습니다: {NEW_CVE_DIR}")
        return entries

    for file in tqdm(os.listdir(NEW_CVE_DIR), desc="Loading new CVE files"):
        if not file.endswith(".json"):
            continue
        file_path = os.path.join(NEW_CVE_DIR, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                cve_data = json.load(f)
                cve_id = cve_data.get("cve", {}).get("CVE_data_meta", {}).get("ID", file)
                desc_list = cve_data.get("cve", {}).get("description", {}).get("description_data", [])
                desc = desc_list[0]["value"] if desc_list else "No description"
                text = f"[CVE] {cve_id}: {desc}"
                entries.append(text)
        except Exception as e:
            print(f"[!] {file} 읽는 중 오류: {e}")
    print(f"[+] 새 CVE {len(entries)}개 로드 완료.")
    return entries

# === 함수: 임베딩 생성 ===
def get_embeddings(texts):
    embeddings = []
    for text in tqdm(texts, desc="Generating embeddings"):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            emb = np.array(response.data[0].embedding, dtype=np.float32)
            embeddings.append(emb)
        except Exception as e:
            print(f"[!] Embedding 실패 ({text[:50]}...): {e}")
    return np.array(embeddings)

# === 메인 로직 ===
def update_faiss_with_new_cve():
    if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
        print("[!] 기존 FAISS 인덱스 또는 메타 파일을 찾을 수 없습니다.")
        return

    print("[*] 기존 인덱스 로드 중...")
    index = faiss.read_index(INDEX_PATH)
    with open(META_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    print(f"[+] 기존 메타데이터 항목: {len(metadata)}개")

    new_entries = load_new_cve_entries()
    if not new_entries:
        print("[!] 추가할 새 CVE 데이터가 없습니다.")
        return

    print("[*] 새 CVE 임베딩 생성 중...")
    new_vectors = get_embeddings(new_entries)
    print(f"[+] 새 임베딩 완료. Shape: {new_vectors.shape}")

    print("[*] FAISS 인덱스에 새 데이터 추가 중...")
    index.add(new_vectors)
    metadata.extend(new_entries)

    print("[*] 인덱스 및 메타데이터 저장 중...")
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"[✓] 인덱스 업데이트 완료: {INDEX_PATH}")
    print(f"[✓] 메타데이터 업데이트 완료: {META_PATH}")
    print(f"[✓] 전체 데이터 수: {len(metadata)}개")

# === 실행 ===
if __name__ == "__main__":
    update_faiss_with_new_cve()
