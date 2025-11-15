import os
import json
import faiss
import numpy as np
from openai import OpenAI

# === 패키지 경로 설정 ===
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import log_event

# === OpenAI API 키 설정 ===
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("[!] OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
client = OpenAI(api_key=api_key)

# === 경로 설정 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
VECTOR_DIR = os.path.join(BASE_DIR, "vectorstore")

INDEX_PATH = os.path.join(VECTOR_DIR, "threat_knowledge.index")
META_PATH = os.path.join(VECTOR_DIR, "threat_knowledge_meta.json")

# === FAISS 인덱스 및 메타데이터 로드 ===
if not os.path.exists(INDEX_PATH) or not os.path.exists(META_PATH):
    raise FileNotFoundError("[!] Vector database not found. Run build_faiss_vector_db_openai.py first.")

print("[*] Loading FAISS index and metadata...")
index = faiss.read_index(INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)
print(f"[+] Vector DB loaded. Entries: {len(metadata)}")

# === 텍스트 임베딩 ===
def get_embedding(text: str) -> np.ndarray:
    """입력 텍스트를 벡터화"""
    try:
        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000]
        )
        return np.array(res.data[0].embedding, dtype=np.float32)
    except Exception as e:
        log_event("Embedding error", str(e))
        print(f"[!] Embedding failed: {e}")
        return np.zeros((1536,), dtype=np.float32)

# === RAG 검색 ===
def search_similar(query: str, top_k: int = 5):
    """FAISS 벡터 검색 (L2 distance 기반)"""
    query_vec = get_embedding(query).reshape(1, -1)
    D, I = index.search(query_vec, top_k)
    results = [
        {"text": metadata[i], "score": float(D[0][n])}
        for n, i in enumerate(I[0]) if i < len(metadata)
    ]
    results = sorted(results, key=lambda x: x["score"])  # 거리 낮을수록 유사
    return results

# === GPT 요약 ===
def summarize_results(query: str, results: list):
    """RAG 검색 결과를 기반으로 보안 분석 요약"""
    context_texts = "\n\n".join([r["text"] for r in results])
    prompt = f"""
당신은 사이버 보안 분석가입니다.
다음은 사용자가 질의한 내용과, 관련된 MITRE ATT&CK 및 CVE 데이터입니다.

사용자 질의:
{query}

관련 데이터:
{context_texts}

다음 내용을 한국어로 기술적으로 요약하세요:
1. 취약점 요약 (무엇이 문제인가?)
2. 관련 공격 기법 또는 CVE
3. 대응 및 완화 방법
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 사이버 위협 분석 전문가이다."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        log_event("Summarization error", str(e))
        print(f"[!] Summarization detailed error: {e}")
        return "[!] 요약 생성 실패"

# === 통합 RAG 질의 ===
def rag_query(query: str):
    log_event("RAG Query Received", query)
    results = search_similar(query)
    summary = summarize_results(query, results)
    log_event("RAG Query Completed", f"{len(results)} results summarized")
    return {"query": query, "top_results": results, "summary": summary}

# === 실행 테스트 ===
if __name__ == "__main__":
    print("[*] RAG Agent test mode")
    user_query = input("검색할 보안 관련 문장을 입력하세요: ")
    result = rag_query(user_query)

    print("\n=== 검색 결과 ===")
    for r in result["top_results"]:
        print(f"- (dist={r['score']:.4f}) {r['text'][:120]}...")

    print("\n=== 요약 결과 ===")
    print(result["summary"])
