# 채널 플레이북 — 홈페이지 / 자체 도메인 사이트

> 회사·브랜드의 대표 도메인. 테크니컬 SEO 비중이 가장 크고, 다른 모든 채널(블로그, 상세페이지)의 최종 착지점이자 정본(canonical) 후보 1순위.

---

## 1. 우선순위

| 순위 | 항목 | 이유 |
|---|---|---|
| 1 | `../01-technical-seo/checklist.md` 전체 항목 | 도메인 전체에 영향 — 여기서 통제권을 가짐 |
| 2 | `Organization` 구조화 데이터 | 회사 신원·신뢰도의 근거(전 채널 공통 참조점) |
| 3 | 사이트 구조(IA)·내부 링크 | 서브페이지(About, 서비스, 블로그, 채용 등)의 관계를 명확히 |
| 4 | 코어 웹 바이탈/성능 | 자체 도메인은 성능 최적화 여지가 가장 큼 |

---

## 2. 사이트 구조(IA) 원칙

- 홈 → 카테고리 → 상세 페이지의 3단 이하 클릭 구조 권장(깊을수록 크롤링·색인 불리)
- URL 구조에 카테고리 반영: `example.com/service/`, `example.com/blog/{slug}/`
- 브레드크럼(`BreadcrumbList` 스키마) 적용 — `../01-technical-seo/structured-data-jsonld.md`
- About/연락처 페이지는 E-E-A-T 신호로 필수 — 회사 정보, 대표자, 사업자등록 정보 등

---

## 3. 홈페이지에 넣을 구조화 데이터

| 스키마 | 위치 |
|---|---|
| `Organization` | 홈 또는 About 페이지 1회 |
| `WebSite` (+ `SearchAction` — 사이트 내 검색 있을 시) | 홈페이지 |
| `BreadcrumbList` | 서브페이지 전체 |
| 개별 서비스/상품 페이지 스키마 | 해당 상세페이지 (`../04-channel-playbooks/detail-landing-page.md` 참조) |

---

## 4. 블로그 서브디렉토리 운영 시

블로그를 별도 플랫폼(네이버, 브런치 등)이 아니라 `example.com/blog/` 형태로 자체 도메인에 붙이면 도메인 권위(DA)가 홈페이지로 그대로 축적된다. 가능하면 이 구조를 정본으로 채택 — `../02-content-seo/cross-publishing.md` 참조.

---

## 5. 발행 전 체크리스트

- [ ] 전체 사이트 HTTPS
- [ ] 사이트맵 제출 + 서치콘솔 연동
- [ ] 페이지별 고유 title/description
- [ ] `Organization` 스키마 적용
- [ ] 내부 링크로 고아 페이지 없음
- [ ] 모바일 대응 확인
- [ ] Lighthouse Performance 70+/SEO 90+
