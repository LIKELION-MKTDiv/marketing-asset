"""
Slack 알림 유틸리티.
Webhook 또는 Bot Token 방식 모두 지원.
"""
import json
import aiohttp
from config import SLACK_WEBHOOK_URL, SLACK_BOT_TOKEN, SLACK_CHANNEL


async def send_webhook(text: str, blocks: list | None = None) -> bool:
    if not SLACK_WEBHOOK_URL:
        print("[Slack] SLACK_WEBHOOK_URL 미설정 — 전송 생략")
        return False
    payload: dict = {"text": text}
    if blocks:
        payload["blocks"] = blocks
    async with aiohttp.ClientSession() as session:
        resp = await session.post(SLACK_WEBHOOK_URL, json=payload)
        return resp.status == 200


async def send_bot_message(text: str, blocks: list | None = None) -> bool:
    if not SLACK_BOT_TOKEN:
        print("[Slack] SLACK_BOT_TOKEN 미설정 — 전송 생략")
        return False
    payload = {
        "channel": SLACK_CHANNEL,
        "text": text,
    }
    if blocks:
        payload["blocks"] = blocks
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json",
    }
    async with aiohttp.ClientSession() as session:
        resp = await session.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload,
        )
        data = await resp.json()
        return data.get("ok", False)


async def notify(summary: str, notion_url: str, change_stats: dict) -> bool:
    """경쟁사 분석 완료 알림."""
    added = change_stats.get("total_added", 0)
    removed = change_stats.get("total_removed", 0)
    changed = change_stats.get("total_changed", 0)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "📊 KDT 경쟁사 분석 완료"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*신규 부트캠프:* {added}개"},
                {"type": "mrkdwn", "text": f"*종료/삭제:* {removed}개"},
                {"type": "mrkdwn", "text": f"*내용 변경:* {changed}개"},
            ]
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*요약*\n{summary[:600]}"}
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Notion에서 전체 보기"},
                    "url": notion_url,
                    "style": "primary",
                }
            ]
        }
    ]
    # Webhook 우선, 없으면 Bot Token 방식
    if SLACK_WEBHOOK_URL:
        return await send_webhook(f"KDT 경쟁사 분석 완료 — {notion_url}", blocks)
    elif SLACK_BOT_TOKEN:
        return await send_bot_message(f"KDT 경쟁사 분석 완료 — {notion_url}", blocks)
    else:
        print("[Slack] 전송 수단 없음. SLACK_WEBHOOK_URL 또는 SLACK_BOT_TOKEN 설정 필요.")
        return False
