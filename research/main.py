"""
경쟁사 분석 파이프라인 진입점.
CLI: python main.py
"""
import asyncio
import os

# Windows 콘솔 UTF-8: stdout 래핑 대신 환경변수로 설정
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

from agents.orchestrator import run

if __name__ == "__main__":
    asyncio.run(run(verbose=True))
