# resume-pipeline — 멋사 미래이력서 생성 파이프라인 (V2)

KDT 부트캠프 지원자의 자기소개서 + 부트캠프 정보를 조합해 "미래이력서(MD + HTML)"를 생성하는
파이프라인. 이 fork는 렌더러(Phase 4) V2 구조를 공유용으로 정리한 버전이다.

## 3줄 재현 (더미 데이터로 즉시 확인)

```bash
git clone <this-repo>
cd resume-pipeline
pip install -r requirements.txt
python examples/render_demo.py
```

`examples/output/`에 더미 지원자 2명의 미래이력서(HTML+MD, 총 4파일)가 생성된다.

## 왜 재현되는가 — 렌더는 결정적(Deterministic)이다

풀 파이프라인(CSV 추출 → LLM 분류 → LLM 콘텐츠 생성)은 Claude API 호출(비결정적)과 개인
인증(구독 토큰)이 필요해 그대로 재현할 수 없다. 이 fork에도 그 상단 단계(daily_runner·
메일 발송·실제 지원자 데이터)는 포함하지 않았다.

반면 **Phase 4 렌더(`render_html()` / `render_md()`)는 순수 함수**다 — 같은 intermediate
JSON(`_1_extracted.json` / `_2_profile.json` / `_3_content.json`)을 넣으면 항상 같은
HTML/MD가 나온다. `examples/render_demo.py`는 완전히 가공한 더미 intermediate 2세트를 읽어
이 순수 함수를 직접 호출한다 — 클론만 하면 누구나 동일한 결과를 재현할 수 있는 이유다.

- `examples/sample_intermediate/` — 더미 지원자 2명(전부 가상 인물, 실제 지원자 아님)
  - `샘플지원자1` (student 유형) — 학력 섹션 포함 케이스
  - `샘플지원자2` (career_changer 유형) — 자소서에 배경 정보가 없어 학력/배경 섹션이
    **생략**되는 케이스 (환각 금지 원칙 시연)
- `examples/render_demo.py` — 위 더미를 `class_id="kdt-backendj-27th"`로 렌더해
  `examples/output/`에 저장

## V2 구조 요약

V2는 `class_id`가 `V2_COURSES`(현재 `kdt-backendj-27th`)에 포함된 과정에만 적용되는
7섹션 렌더러다. 핵심 원칙 — **"부트캠프 표준이라 전원 동일한 건 파싱하지 말고 고정
블록으로."**

| 섹션 | 출처 |
|---|---|
| 상단 / Summary | 지원자 개인 데이터 |
| 보유 기술 | 하드스킬 = 과정 고정블록(전원 동일) + Soft Skills = 개인 |
| 핵심 역량 및 활동 | 지원자 개인 데이터 |
| 프로젝트 경험 | 과정 공통 고정 블록(`templates/bootcamp_common/{class_id}.md`, 전원 동일) |
| 학력(배경) | 개인 배경 섹션 원제목 그대로 (학생=학력 / 전향자=커리어 전환 등). 데이터 없으면 생략 |
| 교육 이수 내역 / 인턴십 | 과정 공통 고정 블록 |

LLM이 생성하는 지원자별 섹션(기술 스택·프로젝트 포트폴리오)은 포맷이 사람마다 달라 정규식
파싱이 깨지기 쉽다 — 부트캠프 표준이라 전원 동일한 항목(프로젝트·하드스킬)은 파싱 대신
고정 블록으로 렌더하고, 실제로 사람마다 다른 항목(Summary·핵심역량·학력/배경)만 지원자
데이터에서 뽑는다.

상세 렌더 명세·데이터 매핑·새 과정 온보딩 절차·운영 가이드·버그 수정 이력은
[`docs/V2_렌더_명세.md`](docs/V2_렌더_명세.md) 참고 (이 문서가 V2의 SSOT).

## 이 fork에 포함되지 않은 것

원본 운영 파이프라인 중 아래는 개인 데이터·인증·발송 로직을 포함해 이 공유 fork에는
의도적으로 포함하지 않았다:

- `daily_runner.py` — 배치 스케줄 실행기
- `mail_dispatch/` — Gmail 초안 생성
- 실제 지원자 데이터(`data/`, `outputs/`, `_logs/`)
- 시트/드라이브 연동 스크립트

Phase 1~3(추출·프로파일링·콘텐츠 생성)을 포함한 전체 파이프라인 실행은 `main.py` 참고 —
단, `.env`에 `CLAUDE_CODE_OAUTH_TOKEN`(구독 인증, `ANTHROPIC_API_KEY` 아님) 설정과 실제
지원서 CSV가 필요하다.
