"""
Notion API 래퍼.
분석 결과를 Notion 페이지로 정리한다.
"""
from notion_client import AsyncClient
from config import NOTION_TOKEN, NOTION_PARENT_PAGE_ID


def _get_client() -> AsyncClient:
    if not NOTION_TOKEN:
        raise RuntimeError("NOTION_TOKEN 환경변수가 설정되지 않았습니다.")
    return AsyncClient(auth=NOTION_TOKEN)


def _rich_text(content: str) -> list:
    return [{"type": "text", "text": {"content": content[:2000]}}]


def _heading(level: int, text: str) -> dict:
    tag = f"heading_{level}"
    return {"object": "block", "type": tag, tag: {"rich_text": _rich_text(text)}}


def _paragraph(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": _rich_text(text)}}


def _bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rich_text(text)}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


async def create_analysis_page(title: str, sections: list[dict]) -> str:
    """
    Notion에 분석 결과 페이지를 생성한다.

    sections: [{"heading": str, "body": str, "bullets": [str]}]
    Returns: 생성된 페이지 URL
    """
    client = _get_client()

    blocks = []
    for sec in sections:
        if sec.get("heading"):
            blocks.append(_heading(2, sec["heading"]))
        if sec.get("body"):
            blocks.append(_paragraph(sec["body"]))
        for item in sec.get("bullets", []):
            blocks.append(_bullet(item))
        blocks.append(_divider())

    response = await client.pages.create(
        parent={"page_id": NOTION_PARENT_PAGE_ID},
        properties={
            "title": {"title": _rich_text(title)}
        },
        children=blocks,
    )

    page_id = response["id"].replace("-", "")
    return f"https://notion.so/{page_id}"


async def update_or_create_database_entry(
    database_id: str,
    bootcamp_name: str,
    properties: dict,
    blocks: list[dict],
) -> str:
    """데이터베이스 엔트리를 업데이트하거나 새로 생성."""
    client = _get_client()
    # 기존 항목 검색
    query = await client.databases.query(
        database_id=database_id,
        filter={
            "property": "Name",
            "title": {"equals": bootcamp_name}
        }
    )
    if query["results"]:
        page_id = query["results"][0]["id"]
        await client.pages.update(page_id=page_id, properties=properties)
        # 기존 블록 교체는 복잡하므로 새 블록만 append
        if blocks:
            await client.blocks.children.append(block_id=page_id, children=blocks)
        return f"https://notion.so/{page_id.replace('-', '')}"
    else:
        response = await client.pages.create(
            parent={"database_id": database_id},
            properties=properties,
            children=blocks,
        )
        page_id = response["id"]
        return f"https://notion.so/{page_id.replace('-', '')}"
