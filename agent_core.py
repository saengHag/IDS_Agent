# agent_core.py
from config import OPENAI_API_KEY, LLM_MODEL
from datetime import datetime

# from openai import OpenAI
# client = OpenAI(api_key=OPENAI_API_KEY)

def retrieve_similar_docs(attack_type: str, event_text: str):
    """
    공격 유형과 이벤트 텍스트를 기반으로 RAG 검색 (예시)
    """
    return [
        {"source": "MITRE", "id": "T1059", "excerpt": "Command and Scripting Interpreter"},
        {"source": "CVE", "id": "CVE-2023-12345", "excerpt": "SQL injection vulnerability"}
    ]

def analyze_event(event_text: str, ml_result: dict) -> dict:
    """
    ML → RAG → LLM 순서로 종합 분석 후 JSON 결과 리턴
    """
    context = retrieve_similar_docs(ml_result["attack_type"], event_text)

    prompt = f"""
    [Event]
    {event_text}

    [Predicted Attack]
    {ml_result['attack_type']} (Confidence {ml_result['confidence']:.2f})

    [Context]
    {context}

    공격 개요, 근거, 관련 MITRE/CVE, 대응 방안을 JSON으로 정리해줘.
    """

    # 실제 LLM 호출
    # response = client.chat.completions.create(
    #     model=LLM_MODEL,
    #     messages=[{"role":"user","content":prompt}],
    #     response_format={"type":"json_object"}
    # )
    # return response.choices[0].message.parsed

    # 더미 결과
    return {
        "event_id": datetime.utcnow().isoformat(),
        "predicted_attack": ml_result["attack_type"],
        "confidence": ml_result["confidence"],
        "related_mitre": ["T1059"],
        "related_cve": ["CVE-2023-12345"],
        "summary": "웹 입력 필드에서 SQL Injection 시도가 탐지됨.",
        "recommended_action": [
            "입력값 검증 강화",
            "Prepared Statement 사용",
            "보안 패치 적용"
        ]
    }
