from __future__ import annotations

from pathlib import Path

# ── 경로 ──────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT_DIR / "templates"
ASSETS_DIR = ROOT_DIR / "assets"
OUTPUTS_DIR = ROOT_DIR / "outputs"
DATA_DIR = ROOT_DIR / "data"

# ── 모델 전략 ─────────────────────────────────────────
MODEL_FAST = "claude-sonnet-4-6"      # Phase 1, 2 (구조화·분류)
MODEL_DEEP = "claude-opus-4-6"        # Phase 3 (이력서 콘텐츠 생성)
THINKING_BUDGET = 8_000               # Phase 3 extended thinking 예산

# ── 브랜드 상수 ───────────────────────────────────────
BRAND_COLOR_PRIMARY = "#FF7816"
BRAND_COLOR_DARK = "#333333"
BRAND_NAME = "멋쟁이사자처럼"
BRAND_NAME_EN = "Likelion"

# ── LLM 설정 ─────────────────────────────────────────
MAX_TOKENS_SONNET = 4_096
MAX_TOKENS_OPUS = 16_000
