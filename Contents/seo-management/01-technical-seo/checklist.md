# 테크니컬 SEO 마스터 체크리스트 (채널 불문)

> 검색엔진에 색인되는 모든 채널(블로그, 홈페이지, 상세페이지, 마이크로사이트)에 공통 적용. Google 공식 가이드(`SEO Starter Guide`, `SEO Guide for Web Developers`, `In-Depth Guide to How Google Search Works`)와 `KDT_상세페이지_생성모듈_SEO정책_v3.md`를 채널 불문 원칙으로 일반화했다.

---

## 1. 크롤링·색인 (Google이 페이지를 찾고 읽을 수 있는가)

| 항목 | 기준 | 확인 방법 |
|---|---|---|
| robots.txt | 색인 원하는 페이지를 차단하지 않음 | `/robots.txt` 직접 확인 |
| 사이트맵 | XML 사이트맵 존재 + 구글 서치콘솔에 제출됨 | 서치콘솔 > Sitemaps |
| 대표 URL(canonical) | 페이지마다 정확한 `<link rel="canonical">` | 페이지 소스 확인 |
| 색인 허용 여부 | `noindex`가 의도치 않게 걸려있지 않음 (특히 모집종료/임시페이지) | 서치콘솔 > URL 검사 |
| 내부 링크 | 모든 중요 페이지가 사이트 내 다른 페이지에서 링크로 연결됨(고아 페이지 없음) | 사이트 구조 다이어그램 또는 크롤러 툴 |
| URL 구조 | 짧고 읽기 쉬움, 키워드 포함, 불필요한 파라미터 없음 | 예: `/claim/pet-insurance-rejection/` |
| 리다이렉트 | 종료/이동 페이지는 301로 최신 페이지에 연결 (404 방치 금지) | 링크 체커 |
| HTTPS | 전체 사이트 SSL 적용 | 브라우저 자물쇠 아이콘 |

---

## 2. HTML 구조·시맨틱 태그 (검색엔진이 의미를 이해할 수 있는가)

상세 원칙은 `html-semantic-structure.md` 참조. 체크리스트만 요약:

| 항목 | 기준 |
|---|---|
| H1 개수 | 페이지당 정확히 1개 |
| 헤딩 순서 | H1→H2→H3 건너뛰기 없음 |
| 제목/본문 태그 | 큰 글씨라도 의미상 제목이면 `<h1~h6>`, 문단이면 `<p>`. `<div>`/`<span>`으로 흉내내지 않음 |
| 링크/CTA | 클릭 가능한 요소는 `<a href="...">`. `onclick`만 있는 `<div>` 금지 |
| 이미지 | 콘텐츠 이미지는 `<img alt="...">`. 장식만 CSS 배경(`bg-[url()]`) 허용 |
| 섹션 구분 | `<section>`, `<article>`, `<figure>` 등 시맨틱 태그 사용 |
| 모바일 숨김 | `hidden md:block` 등으로 핵심 텍스트(제목·본문·CTA)를 아예 없애지 않음 — 크기 조절은 가능, 존재 자체를 지우면 안 됨 |

---

## 3. 메타데이터 (head)

| 항목 | 기준 |
|---|---|
| 페이지 제목(title) | 50~60자, 핵심 키워드 앞배치, 페이지마다 고유 |
| 메타 디스크립션 | 120~155자, 키워드 + 클릭 유도, 페이지마다 고유 |
| Open Graph / SNS 공유 정보 | og:title, og:description, og:image 설정 (카톡·슬랙·SNS 공유 미리보기용) |
| 언어 설정 | `<html lang="ko">` |
| 뷰포트 | `<meta name="viewport" content="width=device-width, initial-scale=1">` |

---

## 4. 구조화 데이터 (Structured Data / Schema.org)

상세 가이드는 `structured-data-jsonld.md` 참조.

| 항목 | 기준 |
|---|---|
| 페이지 성격에 맞는 스키마 적용 | Organization, Article, FAQPage, Course, Product, BreadcrumbList 중 해당하는 것 |
| JSON-LD 형식 | 마이크로데이터보다 JSON-LD 권장(구글 공식 권장 방식) |
| 구글 Rich Results Test 통과 | 문법 오류 없음 |

---

## 5. 성능 (Core Web Vitals / 로딩 속도)

에셋(이미지) 많은 페이지일수록 중요. 기준은 `KDT_상세페이지_생성모듈_SEO정책_v3.md`에서 검증된 값을 채널 불문 기본값으로 사용.

| 항목 | 기준 |
|---|---|
| 이미지 형식 | WebP 우선 |
| 이미지 용량 | 개당 300KB 이하 (일반 콘텐츠 이미지는 500KB 이하) |
| 전체 페이지 용량 | 10MB 이하 |
| 지연 로딩(lazy load) | 첫 화면 밖 이미지는 지연 로딩 |
| CSS 최적화 | 미사용 스타일 제거(purge) — Tailwind 등 유틸리티 CSS 프레임워크 사용 시 필수 |
| Lighthouse 목표 | Performance 70점 이상, SEO 90점 이상 |

---

## 6. 모바일 대응

| 항목 | 기준 |
|---|---|
| 반응형 | 모든 화면 크기에서 핵심 콘텐츠 접근 가능 |
| 텍스트 크기 | 모바일에서도 읽기 가능한 크기 (자동 확대/축소 불필요) |
| 탭 타겟 | 버튼·링크 간 충분한 간격 (오탭 방지) |
| 모바일 우선 색인 | 구글은 모바일 버전을 기준으로 색인하므로 데스크톱에만 있는 콘텐츠 없어야 함 |

---

## 7. E-E-A-T 신호 (경험·전문성·권위·신뢰)

Google이 명시적으로 "사람을 위한 콘텐츠"(`Creating Helpful, Reliable, People-First Content`)를 우대한다고 밝힌 항목. 테크니컬 요소는 아니지만 색인/순위 판단에 직결되어 여기 포함.

| 항목 | 기준 |
|---|---|
| 작성자/운영주체 정보 | Organization/Person 스키마 또는 명시적 표기 |
| 출처 표기 | 수치·주장에 근거 링크 |
| 연락처/회사 정보 | 홈페이지에 명확히 존재 (About, 연락처) |
| 제3자 SEO 도구·서비스 신뢰 | 순위 보장을 약속하는 업체는 경계 (`Google Search's guidance on using third-party SEO tools`) — 자체 체크리스트 기반 운영을 우선한다 |

---

## 8. 배포 전 자동/수동 점검 항목 (개발팀 체크리스트)

`KDT_상세페이지_생성모듈_SEO정책_v3.md` §4-3에서 검증된 자동 점검 항목을 범용화:

| 체크 항목 | 기준 |
|---|---|
| H1 개수 | 정확히 1개 |
| 헤딩 순서 | 건너뛰기 없음 |
| 모든 `<img>` alt 존재 | 장식 이미지 제외 전부 |
| alt 길이 | 20~50자 |
| `<div>`로 된 제목 없음 | 큰 텍스트인데 heading 태그 아닌 요소 탐지 |
| CTA가 `<a>` 태그인지 | onclick만 있고 href 없는 요소 탐지 |
| title/description 길이 | 각 50~60자 / 120~155자 |
| 이미지 용량 | 개당 300KB 이하 |
