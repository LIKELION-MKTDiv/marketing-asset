# 원본 자료 인덱스

> 이 허브(`01~05`)는 아래 원본 문서들을 통합·일반화한 것이다. 더 깊은 디테일이 필요하면 원본으로 이동할 것. Google 공식 문서는 저작권상 이 허브에 전문을 복제하지 않았으므로, 원문 확인이 필요하면 아래 경로에서 직접 열어볼 것.

---

## 1. Google 공식 SEO/GEO 가이드 — `C:\Users\manid\Documents\whisky\문서 아카이브\SEO GEO\`

| 파일 | 다루는 내용 | 이 허브에서 반영된 곳 |
|---|---|---|
| `SEO Starter Guide The Basics.md` | 구글 공식 SEO 입문 — 크롤링/색인 기초, 사이트 구조, 콘텐츠 품질 기본 원칙 | `../01-technical-seo/checklist.md`, `../00-framework.md` |
| `SEO Guide for Web Developers.md` / `SEO Guide for Web Developers 1.md` | 개발자向 기술 SEO(메타 태그, 구조화 데이터, 크롤링 최적화, 자바스크립트 SEO) | `../01-technical-seo/checklist.md`, `structured-data-jsonld.md` |
| `In-Depth Guide to How Google Search Works.md` | 크롤링→색인→서빙(랭킹) 전체 파이프라인 상세 | `../01-technical-seo/checklist.md` §1 |
| `Creating Helpful, Reliable, People-First Content.md` | E-E-A-T, "사람을 위한 콘텐츠" 품질 가이드라인 | `../01-technical-seo/checklist.md` §7, `../02-content-seo/writing-rules.md` §8 |
| `Optimizing your website for generative AI features on Google Search.md` | AI Overviews/AI 모드 대응 공식 가이드. RAG·쿼리 팬아웃 원리, GEO/AEO 통념 반박 | `../03-geo-aeo/geo-aeo-guide.md` (전체 근거) |
| `Google Search's Guidance on Generative AI Content on Your Website Google Search Central.md` | AI로 생성한 콘텐츠를 웹사이트에 쓸 때의 정책·품질 기준 | `../03-geo-aeo/geo-aeo-guide.md` §3-4 |
| `Google Search's guidance on using third-party SEO tools, services, and advice.md` | 제3자 SEO 툴·컨설팅을 평가하는 기준(순위 보장 주장 등 경계) | `../01-technical-seo/checklist.md` §7, `../03-geo-aeo/geo-aeo-guide.md` §5 |
| `Do you need an SEO.md` | SEO를 자체 운영할지 외주를 줄지 판단하는 의사결정 가이드 | 참고용 — 이 허브에는 직접 반영하지 않음(운영 의사결정은 상황별 판단 필요) |
| `[Frostai]GEO_AEO_Playbook_1편.pdf` | 실무자 관점의 GEO/AEO 전술 모음(민간 자료) | `../03-geo-aeo/geo-aeo-guide.md`의 실전 체크리스트 부분 참고. **Google 공식 입장(통념 반박 섹션)과 상충하는 전술은 이 허브에 반영하지 않았음** — 민간 GEO 자료의 과장된 전술(청킹, llms.txt 등)보다 Google 공식 가이드를 우선했다 |

---

## 2. 기존 프로젝트 SEO 문서 (통합의 원재료)

| 파일 | 성격 | 이 허브에서 반영된 곳 | 원본 유지 이유 |
|---|---|---|---|
| `C:\Users\manid\marketing-asset\Contents\content-project\SEOREADME.md` (`content-project/SEOREADME.md`) | 네이버/브런치/인블로그 3개 플랫폼 콘텐츠 SEO 규약 | `../02-content-seo/writing-rules.md`, `../04-channel-playbooks/blog-*.md` | `content-editor` 등 기존 에이전트가 이미 참조 중 — 프로젝트 히스토리 보존 |
| `문서 아카이브/SEO GEO/KDT_상세페이지_생성모듈_SEO정책_v3.md` (및 v2-1, v2-2, 구버전) | KDT 상세페이지 생성 모듈(BDL/Tailwind 기반) 테크니컬 SEO 정책 | `../01-technical-seo/html-semantic-structure.md`, `../04-channel-playbooks/detail-landing-page.md` | 실제 모듈 협의 이력(BDL/AXP 질문지 등)이 담겨 있어 프로젝트 실행 시 원본 참조 필요 |
| `김태원 인생/반려동물-비즈니스/기획/사이트MVP-3_콘텐츠-SEO-실험.md` | 위올라잇마이펫 워드프레스 SEO 세팅 + AEO 스펙 + 카테고리 IA | `../03-geo-aeo/geo-aeo-guide.md`, `../02-content-seo/cross-publishing.md` | 위올라잇마이펫 전용 카테고리 슬러그·발행 계획은 그 프로젝트에만 해당 |
| `김태원 인생/반려동물-비즈니스/기획/콘텐츠-에디팅-구조.md` | 위올라잇마이펫 콘텐츠 에디팅 SOP(SEOREADME 위에 얹는 델타) | 반영 안 함(비즈니스 특화 톤·컴플라이언스는 이 허브 범위 밖) | `content-editor` 에이전트가 직접 참조하는 프로젝트 SOP로 유지 |
| `likelion-owned-media/.claude/commands/seo-review.md` | 멋쟁이사자처럼 owned media SEO 점검 슬래시 커맨드 | `../05-audit/audit-checklist.md`를 점검 기준 원본으로 참조하도록 업데이트됨 | 커맨드 자체는 그대로 유지, 기준표만 이 허브로 연결 |

---

## 3. 갱신 정책

- Google이 새 공식 가이드를 내면 `문서 아카이브/SEO GEO/`에 원문 추가 → 이 표에 행 추가 → 영향받는 `01/02/03` 문서 업데이트.
- 새 프로젝트에서 채널별 SEO 세부 규칙이 새로 생기면, 먼저 이 허브의 기존 채널 플레이북으로 흡수 가능한지 확인 후, 안 되면 `../04-channel-playbooks/`에 새 파일 추가.
- 민간 GEO/AEO 자료(플레이북, 유료 툴 마케팅 자료 등)를 반영할 때는 반드시 Google 공식 가이드의 "통념 반박" 섹션과 대조해서 상충하지 않는지 확인할 것(`../03-geo-aeo/geo-aeo-guide.md` §2).
