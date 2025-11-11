from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# 현재 파일이 위치한 디렉토리(AISECURIT)를 루트 디렉토리로 설정
PROJECT_ROOT = Path(__file__).resolve().parent

# 하위 폴더 경로
DATASETS_DIR = PROJECT_ROOT / "datasets"
VECTORS_DIR = PROJECT_ROOT / "data_vectors"
LOG_DIR = PROJECT_ROOT / "logs"
OUTPUT_DIR = LOG_DIR / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"
SNORT_LOG_PATH = PROJECT_ROOT / "snort_logs" / "alert.log"

# OpenAI 관련 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")        # 실행할 API 키 넣으면 됨
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"

# 하위 폴더들이 존재하지 않을 경우 생성한다.
for p in [DATASETS_DIR, VECTORS_DIR, LOG_DIR, OUTPUT_DIR, MODELS_DIR]:
    p.mkdir(parents=True, exist_ok=True)