"""
캐시 관리: 이전 조사 결과를 JSON으로 저장하고, 변경분만 탐지한다.
"""
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from config import CACHE_DIR


def _cache_path(competitor_key: str) -> Path:
    return CACHE_DIR / f"{competitor_key}.json"


def load_cache(competitor_key: str) -> dict | None:
    path = _cache_path(competitor_key)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_cache(competitor_key: str, data: dict) -> None:
    path = _cache_path(competitor_key)
    data["cached_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def bootcamp_id(bootcamp: dict) -> str:
    """부트캠프 이름+트랙을 해시하여 고유 ID 생성."""
    key = f"{bootcamp.get('name', '')}_{bootcamp.get('track', '')}"
    return hashlib.md5(key.encode()).hexdigest()[:10]


def diff_bootcamps(old_list: list[dict], new_list: list[dict]) -> dict:
    """
    Returns:
        added   - 새로 발견된 부트캠프
        removed - 사라진 부트캠프
        changed - 내용이 변경된 부트캠프 (old, new 쌍)
        unchanged - 변경 없는 부트캠프
    """
    old_map = {bootcamp_id(b): b for b in old_list}
    new_map = {bootcamp_id(b): b for b in new_list}

    added, removed, changed, unchanged = [], [], [], []

    for bid, camp in new_map.items():
        if bid not in old_map:
            added.append(camp)
        else:
            old_snap = json.dumps(old_map[bid], sort_keys=True)
            new_snap = json.dumps(camp, sort_keys=True)
            if old_snap != new_snap:
                changed.append({"old": old_map[bid], "new": camp})
            else:
                unchanged.append(camp)

    for bid, camp in old_map.items():
        if bid not in new_map:
            removed.append(camp)

    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }
