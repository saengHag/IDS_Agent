class LLMAgent:
    def __init__(self, model_name="gpt-4o-mini"):
        self.model_name = model_name
        # TODO: LLM API 키 또는 로컬 모델 연결 설정

    def summarize(self, ml_result: dict, rag_data: list) -> dict:
        # TODO: RAG + ML 결과를 기반으로 리포트 생성
        return {
            "summary": f"Detected {ml_result['attack_type']} with confidence {ml_result['confidence']}.",
            "recommendation": "Isolate affected hosts and block suspicious IPs.",
            "references": rag_data
        }
