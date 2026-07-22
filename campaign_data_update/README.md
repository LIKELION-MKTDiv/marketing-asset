# 매체 광고 자동화 (Campaign Data Update)

네이버 SA · 구글 Ads · 메타 · 틱톡 4개 매체의 광고 성과 데이터를 매일 자동 수집해서 구글시트에 반영하는 자동화입니다.

> 담당자가 부재하거나 교체되어도 계속 돌아갈 수 있도록, API 키는 코드가 아니라 GitHub Secrets에 보관합니다.

---

## 한눈에 보기

| 항목 | 내용 |
|------|------|
| 수집 대상 매체 | 네이버 SA, 구글 Ads(검색/디스플레이·동영상/PMax), 메타, 틱톡 |
| 실행 방식 | `python main.py` (로컬) 또는 GitHub Actions 워크플로우 |
| 반영 위치 | 구글시트 `1Nqsc6xvHu-V1u7jyAgPvS1il0jIs9LK6cGRs4f98Qro` → `[RAW] 매체 데이터` 시트 |
| 실패 알림 | 슬랙 웹훅으로 자동 전송 |

---

## 언제 자동 실행되나

이중 구조로 스케줄링되어 있습니다.

1. **`.github/workflows/campaign_data_update.yml`의 `schedule:`** — GitHub Actions 자체 cron (UTC 11:00, UTC 17:00 = 한국시간 20:00, 02:00)
2. **외부 서비스 `cron-job.org`** — 매일 한국시간 **08:50, 14:50**에 `repository_dispatch` 이벤트를 보내 이 워크플로우를 실행시킴 (cron-job.org 계정: 담당 마케터 개인 계정으로 등록되어 있음, Actions 탭에서 "Ads Automation Trigger"로 실행 이력 확인 가능)

⚠️ **주의**: GitHub은 레포에 60일 이상 push(코드 업데이트)가 없으면 `schedule:` cron을 자동으로 꺼버립니다. 이 레포는 팀에서 계속 활발히 사용 중이라 당장 문제는 없지만, 혹시 워크플로우가 안 도는 것 같으면 레포 Actions 탭에서 워크플로우가 `disabled`로 바뀌어 있는지부터 확인하세요 (`Re-enable workflow` 버튼으로 바로 복구 가능).

---

## 필요한 GitHub Secrets

아래 값들은 이 레포의 **Settings → Secrets and variables → Actions**에 등록되어 있습니다. 값 자체는 등록 후 누구도 다시 볼 수 없고, 재발급이 필요하면 아래 "발급처"에서 새로 받아 값만 덮어쓰면 됩니다.

| Secret 이름 | 용도 | 발급처 |
|---|---|---|
| `NAVER_CUSTOMER_ID` / `NAVER_API_KEY` / `NAVER_SECRET` | 네이버 검색광고 API 인증 | 네이버 검색광고 관리자센터 → 도구 → API 사용 관리 |
| `GOOGLE_DEVELOPER_TOKEN` / `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` / `GOOGLE_REFRESH_TOKEN` / `GOOGLE_LOGIN_CUSTOMER_ID` / `GOOGLE_CUSTOMER_ID` | 구글 Ads API 인증 | 구글 Ads API 센터 + 구글 클라우드 콘솔 (OAuth 클라이언트) |
| `META_TOKEN` / `META_AD_ACCOUNT_ID` / `META_API_VER` | 메타 마케팅 API 인증 | 메타 비즈니스 → 시스템 사용자 → 액세스 토큰 |
| `TIKTOK_TOKEN` / `TIKTOK_AD_ACCOUNT_ID` | 틱톡 비즈니스 API 인증 | 틱톡 비즈니스 → 액세스 토큰 관리 |
| `SLACK_WEBHOOK_URL` | 성공/실패 알림 전송 | 슬랙 앱 관리 → Incoming Webhooks |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 구글시트 쓰기 권한 (서비스 계정) | 구글 클라우드 콘솔 프로젝트 `ga4-bigquery-377201` → IAM 및 관리자 → 서비스 계정 → 키 |

---

## 수동으로 다시 실행하고 싶을 때

레포 상단 **Actions** 탭 → `Campaign Data Update (Ads Automation)` 워크플로우 선택 → **Run workflow** 버튼.

---

## 히스토리

- 2026-07-22: 개인 계정(`ad-report-automation`)에 하드코딩되어 있던 API 키를 GitHub Secrets로 이전하고, 이 레포(`campaign_data_update/`)로 이관.
