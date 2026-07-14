"""
precise_review.py — ALF 해결률·첫응답시간 케이스별 자동 검수(Claude API 배치 호출)

methodology/tuesday_template.md에 정리된, 사람이 매주 화요판에서 상담요약을 직접 읽고
판단하던 규칙(구조적 제외 카테고리, 전화처리/중복재오픈 제외 등)을 그대로 프롬프트에 반영해
Claude에 배치로 판정시킨다. 월요판 헤드라인에서 태그 기반 근사치 대신 이 결과를 쓴다.

API 실패 시(키 없음/네트워크 오류/응답 파싱 실패) None을 반환 — 호출부는 이 경우
기존 태그 기반 근사치로 조용히 폴백해야 한다(리포트 발송 자체를 막으면 안 됨).
"""

import json
import os
import re

import requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = 'claude-sonnet-5'
ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages'

ALF_SYSTEM_PROMPT = """너는 VOC(고객문의) 상담 케이스를 검토해서 ALF(챗봇) 해결률 계산에서
제외할 케이스를 판정하는 시니어 CX 분석가다.

아래 5개 카테고리 중 하나에 해당하면 "정책상 인적처리 필수"로 보고 구조적 제외 대상(exclude=true)이다:
1. 환불/결제 처리 요청 — 환불 완료 안내, 영수증 발급, 결제수단 변경, 재결제
2. 결제/정책 확인 — 국취제, 내일배움카드 자부담금, 훈련장려금 등 복잡한 정책 확인
3. 수강철회·취소·과정변경 — 수강 철회, 다른 과정으로 변경 희망
4. 계정 처리 — 이메일 변경, 회원 탈퇴
5. 개인 상태·신청현황 확인 — 합격여부, 수강신청 처리여부, 선발상태 등 본인 계정 상태 확인

주의사항:
- 익명 방문자(닉네임이 "단어+숫자3자리" 패턴)라는 이유만으로 제외하지 말 것 — 반드시 상담요약 내용으로 판단.
- 위 5개 카테고리에 명확히 해당하지 않으면 제외하지 말 것(exclude=false). 애매하면 포함(exclude=false)이 기본값.
- 단순 피드백(CSAT 자동 메시지 등 실질 문의 없음)은 구조적 제외 대상이 아님(exclude=false) — 애초에 매니저가 처리할 필요가 없었던 것과는 다른 판단이므로 이 카테고리 판정에서는 건드리지 않는다.

입력은 번호가 매겨진 케이스 목록이다(각 줄: "N. [chatId=...] 상담요약").
반드시 JSON 배열만 출력하라. 다른 텍스트를 앞뒤로 붙이지 말 것.
각 원소 형식: {"chatId": "...", "exclude": true 또는 false, "category": "카테고리명 또는 null"}"""

FRT_SYSTEM_PROMPT = """너는 VOC(고객문의) 상담의 첫 응답시간 극단치를 검토하는 시니어 CX 분석가다.

아래 목록은 첫 응답시간이 15분을 넘긴 케이스들이다(운영시간 기준으로 이미 정규화된 값).
각 케이스의 상담요약을 읽고, 다음 중 하나에 해당하면 평균 계산에서 제외 대상(exclude=true)이다:
- "유선으로 안내 완료", "전화로 처리" 등 실제 응대가 채팅 밖(전화)에서 이미 끝났고 채팅상 응답시각은 사후 메모일 뿐인 경우
- "중복 채팅 건", "앞선 상담창 안내" 등 같은 문의의 재오픈 건이라 독립된 지연 케이스로 보면 안 되는 경우

주의사항:
- "고객이 며칠 뒤 재문의"처럼 시간 간격만으로 자동 판단하지 말 것 — 반드시 상담요약 내용에 위 사유가 명시됐을 때만 제외.
- 애매하면 제외하지 말 것(exclude=false)이 기본값 — 진짜 지연이면 그대로 카운트에 남아야 한다.

입력은 번호가 매겨진 케이스 목록이다(각 줄: "N. [chatId=...] 응답시간=M분 상담요약").
반드시 JSON 배열만 출력하라. 다른 텍스트를 앞뒤로 붙이지 말 것.
각 원소 형식: {"chatId": "...", "exclude": true 또는 false, "reason": "사유 또는 null"}"""


def _call_claude(system, user_text, max_tokens=4096):
    if not ANTHROPIC_API_KEY:
        return None
    headers = {
        'x-api-key': ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
    }
    body = {
        'model': ANTHROPIC_MODEL,
        'max_tokens': max_tokens,
        'system': system,
        'messages': [{'role': 'user', 'content': user_text}],
    }
    r = requests.post(ANTHROPIC_URL, headers=headers, json=body, timeout=180)
    r.raise_for_status()
    return r.json()['content'][0]['text']


def _extract_json_array(text):
    """모델이 코드블록(```json ... ```)으로 감싸서 답할 수도 있어 대괄호 구간만 뽑아 파싱."""
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(0))


def review_alf_exclusions(agent_cases):
    """agent_cases: [{'chatId': str, '상담요약': str}, ...] (처리구분='상담원연결' 전체)
    반환: 구조적 제외 대상 chatId의 set. 실패 시 None(호출부가 태그 기반 근사치로 폴백)."""
    if not agent_cases:
        return set()
    numbered = "\n".join(
        f"{i+1}. [chatId={c['chatId']}] {(c['상담요약'] or '')[:400]}"
        for i, c in enumerate(agent_cases)
    )
    try:
        text = _call_claude(ALF_SYSTEM_PROMPT, numbered)
        if text is None:
            return None
        parsed = _extract_json_array(text)
        if parsed is None:
            return None
        return {str(item['chatId']) for item in parsed if item.get('exclude')}
    except Exception:
        return None


def review_frt_exclusions(delayed_cases):
    """delayed_cases: [{'chatId': str, '상담요약': str, '응답분': float}, ...]
    (응답시간 15분 이상인 케이스만) 반환: 평균 계산에서 뺄 chatId의 set. 실패 시 None."""
    if not delayed_cases:
        return set()
    numbered = "\n".join(
        f"{i+1}. [chatId={c['chatId']}] 응답시간={c['응답분']:.0f}분 {(c['상담요약'] or '')[:400]}"
        for i, c in enumerate(delayed_cases)
    )
    try:
        text = _call_claude(FRT_SYSTEM_PROMPT, numbered)
        if text is None:
            return None
        parsed = _extract_json_array(text)
        if parsed is None:
            return None
        return {str(item['chatId']) for item in parsed if item.get('exclude')}
    except Exception:
        return None
