import os
import json
import faiss
import numpy as np
from tqdm import tqdm
from openai import OpenAI

# API KEY 임시로 달아놓음. 올릴 때는 꼭 떼야함...
os.environ["OPENAI_API_KEY"] = ""

# === OpenAI 클라이언트 ===
client = OpenAI()

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_DIR, "datasets")
CVE_DIR = os.path.join(DATA_DIR, "cve-json")
MITRE_PATH = os.path.join(DATA_DIR, "enterprise-attack.json")

VECTOR_DIR = os.path.join(PROJECT_DIR, "models", "vectorstore")
os.makedirs(VECTOR_DIR, exist_ok=True)

# === 벡터화 대상 수집 ===
entries = []

# --- MITRE ATT&CK 데이터 ---
if os.path.exists(MITRE_PATH):
    print(f"[+] Loading MITRE ATT&CK data: {MITRE_PATH}")
    with open(MITRE_PATH, "r", encoding="utf-8") as f:
        mitre_data = json.load(f)
        for obj in mitre_data.get("objects", []):
            if obj.get("type") in ["attack-pattern", "malware", "tool", "intrusion-set"]:
                name = obj.get("name", "Unnamed")
                desc = obj.get("description", "")
                text = f"[MITRE] {name}: {desc}"
                entries.append(text)
else:
    print(f"[!] MITRE ATT&CK file not found at: {MITRE_PATH}")

# --- CVE 데이터 ---
if os.path.exists(CVE_DIR):
    print(f"[+] Loading CVE JSON files from: {CVE_DIR}")
    for file in tqdm(os.listdir(CVE_DIR), desc="Loading CVE files"):
        if file.endswith(".json"):
            file_path = os.path.join(CVE_DIR, file)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    cve_data = json.load(f)
                    cve_id = cve_data.get("cve", {}).get("CVE_data_meta", {}).get("ID", file)
                    desc_list = cve_data.get("cve", {}).get("description", {}).get("description_data", [])
                    desc = desc_list[0]["value"] if desc_list else "No description"
                    text = f"[CVE] {cve_id}: {desc}"
                    entries.append(text)
            except Exception as e:
                print(f"[!] Error reading {file}: {e}")
else:
    print(f"[!] CVE JSON folder not found: {CVE_DIR}")

print(f"[+] Total entries collected: {len(entries)}")

# === OpenAI Embedding 생성 ===
def get_embedding_batch(texts):
    vectors = []
    for text in tqdm(texts, desc="Embedding"):
        try:
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8000]
            )
            emb = np.array(response.data[0].embedding, dtype=np.float32)
            vectors.append(emb)
        except Exception as e:
            print(f"[!] Embedding failed for text: {text[:60]}... -> {e}")
    return np.array(vectors)

print("[*] Generating embeddings with OpenAI...")
embeddings = get_embedding_batch(entries)
print(f"[+] Embedding complete. Shape: {embeddings.shape}")

# === FAISS 인덱스 생성 ===
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)

# === 저장 ===
index_path = os.path.join(VECTOR_DIR, "threat_knowledge.index")
meta_path = os.path.join(VECTOR_DIR, "threat_knowledge_meta.json")

faiss.write_index(index, index_path)
with open(meta_path, "w", encoding="utf-8") as f:
    json.dump(entries, f, indent=2, ensure_ascii=False)

print(f"[✓] Unified vector index saved to: {index_path}")
print(f"[✓] Metadata saved to: {meta_path}")
