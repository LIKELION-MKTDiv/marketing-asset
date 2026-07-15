# CLAUDE.md — SEO 관리·점검 전략 허브

이 프로젝트는 여러 프로젝트에 흩어져 있던 SEO 관련 문서(콘텐츠 SEO 규약, 상세페이지 테크니컬 SEO 정책, GEO/AEO 스펙, Google 공식 가이드)를 **하나의 참조 허브**로 통합한 것입니다. 목적은 두 가지입니다.

1. **어떤 비즈니스 상황·채널에서도** 테크니컬 SEO와 콘텐츠 SEO를 일관된 기준으로 점검할 수 있게 한다.
2. **기존에 만들어둔 SEO 관련 에이전트**(`content-editor`, `research-analyst`, `interactive-builder` 등)가 이 허브를 공통 참조 규약으로 로드해서 쓰게 한다.

이 프로젝트 자체는 실행 코드가 없는 **문서 허브**입니다(`likelion-owned-media/`와 동일한 성격).

---

## 왜 통합했는가

- `content-project/SEOREADME.md` — 네이버·브런치·인블로그용 **콘텐츠 SEO** 구조 규약만 다룸
- `문서 아카이브/SEO GEO/KDT_상세페이지_생성모듈_SEO정책_v3.md` — KDT 상세페이지 모듈 한정 **테크니컬 SEO** 정책
- `반려동물-비즈니스/기획/사이트MVP-3_콘텐츠-SEO-실험.md` — 위올라잇마이펫 한정 SEO/AEO 실행 스펙
- `문서 아카이브/SEO GEO/*.md` — Google 공식 SEO/GEO 가이드 원문(사이트 종류 불문 범용 원칙)

이 문서들은 각각 특정 프로젝트·플랫폼에 종속돼 있어서, 새 채널(인스타그램·유튜브·틱톡 등)이나 새 비즈니스가 생길 때마다 처음부터 다시 정리해야 했습니다. 이 허브는 **채널 불문 공통 원칙**과 **채널별 적용 규칙**을 분리해서, 새 채널이 추가돼도 공통 원칙은 그대로 두고 채널 플레이북만 추가하면 되도록 설계했습니다.

---

## 폴더 구조

```
seo-management/
├── 00-framework.md              테크니컬 SEO vs 콘텐츠 SEO vs GEO/AEO 전체 지도. 가장 먼저 읽을 문서
├── 01-technical-seo/            채널 불문 테크니컬 SEO 원칙 (태그 구조·구조화 데이터·성능·색인)
├── 02-content-seo/              채널 불문 콘텐츠 SEO 원칙 (헤딩·키워드·본문·이미지·교차발행)
├── 03-geo-aeo/                  생성형 AI 검색(챗GPT·퍼플렉시티·구글 AI 개요) 대응 원칙
├── 04-channel-playbooks/        채널별 적용 규칙 (블로그 3종·홈페이지·상세페이지·마이크로사이트·인스타그램·유튜브·틱톡)
├── 05-audit/                    점검 체크리스트 + 리포트 템플릿
├── 06-reference/                원본 자료 인덱스 (Google 공식 문서·기존 프로젝트 문서 위치와 요약)
└── .claude/commands/seo-audit.md   슬래시 커맨드
```

**읽는 순서**: `00-framework.md` → 상황에 맞는 `01/02/03` 원칙 → 해당 `04-channel-playbooks/` 채널 문서 → 발행 전 `05-audit/audit-checklist.md`로 점검.

---

## 이 허브를 쓰는 에이전트

| 에이전트 | 위치 | 이 허브에서 참조할 것 |
|---|---|---|
| `content-editor` | `C:\Users\manid\.claude\agents\content-editor.md` | `02-content-seo/writing-rules.md` + `04-channel-playbooks/blog-inblog.md`(또는 발행 채널) + `03-geo-aeo/geo-aeo-guide.md` |
| `research-analyst` | `C:\Users\manid\.claude\agents\research-analyst.md` | `05-audit/audit-checklist.md`(SERP 경쟁 벤치마크 항목) |
| `interactive-builder` | `C:\Users\manid\.claude\agents\interactive-builder.md` | `01-technical-seo/html-semantic-structure.md` + `01-technical-seo/structured-data-jsonld.md`(단일 HTML 산출물도 시맨틱 태그·스키마 적용) |
| `likelion-owned-media` `/seo-review` 커맨드 | `C:\Users\manid\likelion-owned-media\.claude\commands\seo-review.md` | `05-audit/audit-checklist.md`를 점검 기준 원본으로 참조 |

각 에이전트/커맨드 파일은 이 허브의 구체 파일 경로를 "반드시 먼저 로드할 참조 규약"으로 명시하도록 업데이트되어 있습니다. 기존 프로젝트 전용 SOP(`콘텐츠-에디팅-구조.md` 등)는 삭제하지 않고, 이 허브의 공통 규칙 위에 얹는 "델타" 문서로 유지합니다.

---

## 원본 문서와의 관계 (중요)

이 허브는 기존 문서를 **대체하지 않고 통합·일반화**합니다.

- `content-project/SEOREADME.md`, `KDT_상세페이지_생성모듈_SEO정책_v3.md` 등 원본은 그대로 유지됩니다(프로젝트별 히스토리·의사결정 기록으로서 가치가 있음).
- 이 허브의 문서들은 원본에서 **채널 종속적인 세부사항을 제거하고 재사용 가능한 원칙으로 추출**한 것입니다. 원본 대비 더 구체적인 실행 규칙이 필요하면 `06-reference/source-index.md`에서 원본 문서로 이동하세요.
- Google 공식 가이드(`문서 아카이브/SEO GEO/`)는 저작권상 원문을 그대로 복제하지 않고, 이 허브에서는 핵심 원칙만 재정리했습니다. 원문 확인이 필요하면 `06-reference/source-index.md`의 경로를 따라가세요.

---

## 유지보수 원칙

- 새 채널이 생기면 `04-channel-playbooks/`에 파일 하나 추가 (공통 원칙 `01/02/03`은 건드리지 않음).
- Google 정책이 바뀌면(코어 업데이트, GEO 관련 신규 가이드 등) `06-reference/source-index.md`에 원본 추가 → 영향받는 `01/02/03` 문서 업데이트.
- 특정 비즈니스 전용 규칙(컴플라이언스, 브랜드 톤 등)은 이 허브에 넣지 말고 해당 프로젝트의 SOP 문서(`콘텐츠-에디팅-구조.md` 같은)에 둘 것 — 이 허브는 범용성을 유지해야 재사용 가치가 있음.
