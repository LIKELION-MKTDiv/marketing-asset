import os
import pathlib
from dotenv import dotenv_values

# .env는 이 파일 기준 상위(프로젝트 루트)에서 로드
_BASE = pathlib.Path(__file__).parent
_env = dotenv_values(_BASE / ".env")
# 시스템 환경변수보다 .env 파일 우선 (override)
os.environ.update({k: v for k, v in _env.items() if v})

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

COMPETITORS = {
    "fastcampus_kernel": {
        "name": "패스트캠퍼스 커널",
        "url": "https://kernel.fastcampus.co.kr/",
        "short": "fastcampus",
    },
    "sparta_nbcamp": {
        "name": "스파르타 내일배움캠프",
        "url": "https://nbcamp.spartaclub.kr/",
        "short": "sparta",
    },
    "codeit_sprint": {
        "name": "코드잇 스프린트",
        "url": "https://sprint.codeit.kr/",
        "short": "codeit",
    },
}

OWN_COMPANY = {
    "name": "멋쟁이사자처럼",
    "url": "https://bootcamp.likelion.net/",
    "short": "likelion",
}

# Notion
NOTION_TOKEN = os.getenv("NOTION_TOKEN", "")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID", "")

# Slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#kdt-competitor-analysis")

# Models
RESEARCH_MODEL = "claude-sonnet-4-6"
ANALYSIS_MODEL = "claude-sonnet-4-6"
INSIGHT_MODEL = "claude-opus-4-6"
DOC_MODEL = "claude-sonnet-4-6"

# Paths
BASE_DIR = pathlib.Path(__file__).parent
CACHE_DIR = BASE_DIR / "data" / "cache"
OUTPUT_DIR = BASE_DIR / "outputs"

CACHE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
