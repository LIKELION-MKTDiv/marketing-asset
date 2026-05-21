# 콘텐츠 에이전트 시스템

IT/테크 교육 콘텐츠 마케팅을 위한 AI 에이전트 워크플로우입니다.  
트렌드 조사부터 발행·성과 관리까지 전 과정을 Claude Code에서 실행할 수 있습니다.

---

## 설치 방법

1. 이 `content-agents` 폴더 전체를 내 워크스페이스에 복사합니다.
2. `CLAUDE.md`를 워크스페이스 **루트**에 넣습니다.
3. `.claude/commands/content-agents/content-agents.md`가 아래 구조에 위치하도록 맞춥니다.

```
my-workspace/
├── CLAUDE.md                            ← 워크스페이스 루트에 배치
├── content-agents/
│   └── references/                      ← 에이전트별 상세 지침 (유일한 소스)
│       ├── agent01_트렌드조사.md
│       ├── agent02_트렌드선별.md
│       ├── agent03_콘텐츠에디터.md
│       ├── agent03-1_리서치보강.md
│       ├── agent03-2_브런치워싱.md
│       ├── agent04_콘텐츠검수.md
│       ├── agent05_원소스멀티유즈.md
│       └── agent06_콘텐츠발행성과관리.md
└── .claude/
    └── commands/
        └── content-agents/
            └── content-agents.md        ← 슬래시 명령어용
```

4. Claude Code에서 `/content-agents:content-agents` 입력하면 실행됩니다.

---

## 전체 워크플로우

```
[Agent 01] 트렌드 조사
     ↓
[Agent 02] 트렌드 선별 + 키워드 분석
     ↓
[Agent 03] 채널별 콘텐츠 초안 작성
     ↓
     ├─ [Agent 03-1] 리서치 보강 (선택)
     └─ [Agent 03-2] 브런치 워싱 (브런치 발행 시)
     ↓
[Agent 04] 콘텐츠 검수
     ↓
[Agent 05] 원소스 멀티유즈 전환
     ↓
[Agent 06 — Mode A] D-1 점검 + 카피 최적화
     ↓ 발행
[Agent 06 — Mode B] 성과 리뷰 + 다음 주제 추천
```

---

## 에이전트 선택 가이드

| 요청 상황 | 실행할 에이전트 |
|---|---|
| 주제부터 발굴하고 싶어 | Agent 01 → 02 → 03 |
| 주제는 있는데 키워드를 잡아줘 | Agent 02 → 03 |
| 주제 + 키워드 모두 확정됐어 | Agent 03 바로 시작 |
| 인터뷰 원문이 있어 | Agent 02 모드 2 → 03 |
| 초안 내용이 부족해 | Agent 03-1 |
| 브런치에도 올리고 싶어 | Agent 03-2 |
| 검수해줘 | Agent 04 |
| 다른 채널로 확장하고 싶어 | Agent 05 |
| 내일 발행 전 점검해줘 | Agent 06 Mode A |
| 성과 분석해줘 | Agent 06 Mode B |
| 처음부터 끝까지 다 해줘 | Agent 01 → 06 전체 실행 |

---

## 지원 채널

| 채널 | SEO 기준 |
|---|---|
| 인블로그 (자사 블로그) | 구글 SEO |
| 네이버 블로그 | 네이버 SEO |
| 브런치 | 구글 SEO |
| 인스타그램 | — |
| 유튜브 | — |

---

## 파일 구성

| 파일 | 설명 |
|---|---|
| `CLAUDE.md` | 워크스페이스 루트에 배치 — 톤·타겟·성과 목표 등 공통 상수 자동 로딩 |
| `.claude/commands/content-agents/content-agents.md` | 슬래시 명령어용 메인 스킬 파일 |
| `content-agents/references/` | 에이전트별 상세 지침 파일 (유일한 소스 — 여기를 수정하면 바로 반영) |

---

## 업데이트

`references/` 안의 에이전트 파일을 수정하면 다음 실행부터 자동으로 반영됩니다.  
캐시 없이 매번 최신 파일을 읽는 구조입니다.
