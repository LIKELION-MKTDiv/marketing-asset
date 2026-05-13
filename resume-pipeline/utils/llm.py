from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from config import (
    MAX_TOKENS_OPUS,
    MAX_TOKENS_SONNET,
    MODEL_DEEP,
    MODEL_FAST,
)

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client


def call_sonnet(
    system: str,
    user: str,
    max_tokens: int = MAX_TOKENS_SONNET,
) -> str:
    client = _get_client()
    msg = client.messages.create(
        model=MODEL_FAST,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _extract_text(msg)


def call_opus_streaming(
    system: str,
    user: str,
    log_path: Path | None = None,
    max_tokens: int = MAX_TOKENS_OPUS,
) -> str:
    client = _get_client()
    collected: list[str] = []
    char_count = 0

    with client.messages.stream(
        model=MODEL_DEEP,
        max_tokens=max_tokens,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if hasattr(event.delta, "text"):
                    collected.append(event.delta.text)
                    char_count += len(event.delta.text)
                    if char_count % 200 < len(event.delta.text):
                        print(".", end="", flush=True)

    print()
    final = stream.get_final_message()
    result = _extract_text(final)

    if log_path:
        usage = final.usage
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(
                f"[Opus] input={usage.input_tokens} output={usage.output_tokens}\n"
            )

    return result


def parse_json_response(text: str) -> dict | list | None:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        json_match = re.search(r"[\[{]", cleaned)
        if json_match:
            candidate = cleaned[json_match.start():]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        print(f"[WARN] JSON 파싱 실패, 원문 길이={len(text)}", file=sys.stderr)
        return None


def _extract_text(message: anthropic.types.Message) -> str:
    return "".join(
        block.text for block in message.content if block.type == "text"
    )
