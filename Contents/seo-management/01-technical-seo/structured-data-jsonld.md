# 구조화 데이터 (Structured Data / JSON-LD) 가이드

> 검색엔진과 AI 답변 엔진이 페이지 내용을 "이해"하는 것을 넘어 "구조적으로 파싱"할 수 있게 하는 메타데이터. 리치 스니펫(별점, FAQ 아코디언, 강의 정보 등) 노출과 GEO/AEO(답변 인용) 모두에 영향을 준다. JSON-LD 형식을 표준으로 사용한다(구글 공식 권장 방식, `<head>` 또는 `<body>`에 `<script type="application/ld+json">`로 삽입).

---

## 1. 상황별 스키마 선택

| 상황 | 스키마 타입 | 효과 |
|---|---|---|
| 회사/브랜드 정보 | `Organization` | 검색 결과 지식패널, AI 답변에서 "누가 운영하는가" 근거 |
| 블로그 글, 아티클 | `Article` / `BlogPosting` | 작성자·발행일·수정일 노출, E-E-A-T 신호 |
| 자주 묻는 질문 | `FAQPage` | 검색 결과에 아코디언 형태로 직접 노출, AEO 핵심 요소 |
| 교육과정/강의 상세페이지 | `Course` | 구글 리치 스니펫에 과정 기간·시작일 등 표시 |
| 상품/서비스 | `Product` | 가격·재고·리뷰 별점 노출 |
| 이동 경로 | `BreadcrumbList` | 검색 결과에 경로(카테고리 > 하위) 표시 |
| 사람(작성자, 강사 등) | `Person` | E-E-A-T용 저자 정보 |
| 이벤트 | `Event` | 날짜·장소가 검색 결과에 직접 노출 |
| 리뷰/평점 | `AggregateRating` / `Review` | 별점 노출 |
| 하우투(단계별 가이드) | `HowTo` | 단계별 리치 스니펫 |

---

## 2. 최소 예시

**Organization** (모든 사이트에 홈 또는 About 페이지에 1회 적용)
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "회사/브랜드명",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://instagram.com/...", "https://youtube.com/..."]
}
```

**FAQPage** (콘텐츠 하단 FAQ 섹션에 적용 — AEO 핵심)
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "질문 텍스트",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "명확하고 간결한 답변 텍스트"
      }
    }
  ]
}
```

**Course** (교육과정 상세페이지)
```json
{
  "@context": "https://schema.org",
  "@type": "Course",
  "name": "과정명",
  "description": "과정 설명",
  "provider": { "@type": "Organization", "name": "운영기관" },
  "hasCourseInstance": {
    "@type": "CourseInstance",
    "courseMode": "Blended",
    "startDate": "2026-09-01"
  }
}
```

---

## 3. 적용 원칙

1. **화면에 실제로 보이는 정보만 마크업한다.** 페이지에 없는 내용을 스키마에만 넣는 것(cloaking)은 구글 스팸 정책 위반.
2. **하나의 페이지에 여러 스키마 중첩 가능** — 예: 상세페이지는 `Course` + `FAQPage` + `BreadcrumbList` 동시 적용.
3. **JSON-LD 하나로 통합** — 스크립트 태그를 여러 개 쓰기보다 배열(`@graph`)로 묶는 것을 권장.
4. **배포 전 검증** — 구글 Rich Results Test로 문법 오류 확인 필수.
5. **동적 페이지는 값도 동적으로** — 기수별 시작일, 재고 상태 등은 하드코딩하지 말고 실제 데이터와 동기화.

---

## 4. 담당 주체 (개발팀 협업 시)

`KDT_상세페이지_생성모듈_SEO정책_v3.md`의 역할 분담 원칙을 그대로 적용:

| 역할 | 담당 |
|---|---|
| 어떤 스키마를 쓸지, 값은 무엇인지 결정 | 기획(마케팅) |
| 스키마를 올바른 JSON-LD 형식으로 페이지에 주입 | 개발팀 |
| head 정보 주입 경로 확보 (모듈이 body만 출력하는 구조일 경우) | 개발팀 |

---

## 5. GEO/AEO와의 연결

구조화 데이터, 특히 `FAQPage`와 명확한 `Answer` 텍스트는 생성형 AI 검색(구글 AI 개요, 챗GPT 검색 등)이 답변을 구성할 때 우선적으로 참조하는 소스가 된다. 자세한 내용은 `../03-geo-aeo/geo-aeo-guide.md` 참조.
