# /seo-audit — 통합 SEO/콘텐츠SEO/GEO-AEO 점검

## 역할
지정한 URL 또는 파일을 `seo-management` 허브의 통합 기준(`05-audit/audit-checklist.md`)으로 점검하고, 채널에 맞는 플레이북(`04-channel-playbooks/`)까지 반영해서 리포트를 출력한다.

## 실행 지시

```
다음 대상을 SEO 관점에서 점검해줘: [URL 또는 파일 경로]
채널: [블로그(네이버/브런치/인블로그) / 홈페이지 / 상세페이지 / 마이크로사이트 / 인스타그램 / 유튜브 / 틱톡]

점검 순서:
1. C:\Users\manid\seo-management\00-framework.md 로 이 채널에 어떤 층위(테크니컬/콘텐츠/GEO-AEO)가 적용되는지 확인
2. C:\Users\manid\seo-management\05-audit\audit-checklist.md 의 A/B/C 섹션 중 해당하는 것으로 점검
3. C:\Users\manid\seo-management\04-channel-playbooks\{채널}.md 의 채널별 세부 기준으로 추가 점검
4. C:\Users\manid\seo-management\05-audit\audit-report-template.md 형식으로 결과 출력
```

## 출력 형식

`05-audit/audit-report-template.md`의 표 형식(카테고리/항목/현재상태/문제점/개선제안/우선순위) 그대로 사용. 종합 판단(발행 가능 여부, 최우선 개선 Top 3)까지 포함.
