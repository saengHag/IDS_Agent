from models.ml_agent import MLAgent
from models.rag_agent import RAGAgent
from models.llm_agent import LLMAgent
from utils.parser import parse_snort_log

class AgentCore:
    def __init__(self):
        self.ml_agent = MLAgent()
        self.rag_agent = RAGAgent()
        self.llm_agent = LLMAgent()

    def process_log(self, file_obj):
        parsed_data = parse_snort_log(file_obj)
        ml_result = self.ml_agent.predict(parsed_data)
        rag_context = self.rag_agent.search_related_docs(ml_result["attack_type"])
        llm_report = self.llm_agent.summarize(ml_result, rag_context)
        return llm_report
