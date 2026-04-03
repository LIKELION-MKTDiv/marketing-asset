# Amaranth 출퇴근 체크 — PRD

> 이 문서는 확장프로그램의 전체 동작 명세다.
> 코드 수정 시 이 문서를 기준으로 구현한다.

---

## 1. 개요

### 제품 정의
- **이름**: Amaranth 출퇴근 체크
- **형태**: Chrome 확장프로그램 (Manifest V3)
- **목적**: Amaranth(그룹웨어) 출퇴근 확인 클릭 시 Google Sheets에 자동 기록 + 주간 근무시간 대시보드 제공

### 핵심 문제
- 라이클리온 멤버들이 그룹웨어에서 출퇴근 체크 후 수기로 별도 근무시간을 관리해야 했음
- 주 40시간 기준으로 금요일 예상 퇴근 시간을 매번 계산해야 하는 번거로움

### 대상 사용자
- 라이클리온 마케팅 팀 내부 사용자
- 그룹웨어 URL: `https://gw.likelion.net/*`

---

## 2. 파일 구조

```
Amaranth_Check/
├── manifest.json       # 확장프로그램 설정
├── background.js       # Service Worker: 인증, Sheets API, 데이터 처리
├── content.js          # 그룹웨어 페이지 DOM 감지 (출퇴근 버튼 클릭)
├── popup.html          # 팝업 UI + CSS
├── popup.js            # 팝업 렌더링, 실시간 업데이트
├── options.html        # 설정 페이지 UI + CSS
└── options.js          # 설정 페이지 로직
```

---

## 3. 아키텍처

### 데이터 흐름

```
[그룹웨어 확인 클릭]
      ↓
content.js (DOM 캡처 이벤트)
      ↓ chrome.runtime.sendMessage(recordAttendance)
background.js (Service Worker)
      ↓ Google OAuth2 PKCE 인증
      ↓ Google Sheets API 기록
      ↓ 팝업 자동 열기 (Chrome 127+)
      ↓ 캐시 초기화
      ↓
popup.js (대시보드 렌더링)
      ↓ chrome.runtime.sendMessage(getDashboardData)
background.js → Sheets API 조회 (캐시 5분)
      ↓
renderToday / renderWeekly / renderFriday
      ↓
startLiveUpdates (60초 인터벌)
      ↓
liveUpdateAll (실시간 반영)
```

### 스토리지 구분

| 키 | 저장소 | 내용 |
|---|---|---|
| `auth` | `chrome.storage.local` | OAuth 토큰 (access_token, refresh_token, expires_at) |
| `dashboardCache` | `chrome.storage.local` | 대시보드 API 응답 캐시 (TTL: 5분) |
| `lastRecord` | `chrome.storage.local` | 마지막 출퇴근 기록 |
| `clientId` | `chrome.storage.sync` | Google OAuth Client ID |
| `clientSecret` | `chrome.storage.sync` | Google OAuth Client Secret |
| `spreadsheetId` | `chrome.storage.sync` | Google Sheets ID |
| `sheetName` | `chrome.storage.sync` | 출퇴근 시트 이름 (기본값: `출퇴근 기록부`) |

> **중요**: `chrome.storage.local`/`sync`는 확장프로그램 파일과 분리된 크롬 내부 저장소다. 파일(알집) 교체 시 데이터가 보존된다.

---

## 4. Google Sheets 구조

### 시트 목록

| 시트명 | 컬럼 구조 | 용도 |
|---|---|---|
| `출퇴근 기록부` (설정 가능) | A: 날짜(YYYY-MM-DD), B: 출근(HH:MM), C: 퇴근(HH:MM) | 실제 출퇴근 기록 |
| `공휴일` | A: 날짜(YYYY-MM-DD), B: 공휴일명 | 공휴일 정보 |
| `반차/연차` | A: 날짜(YYYY-MM-DD), B: 종류(`반차` 또는 `연차`) | 휴가 기록 |
| `WeeklySettings` | A: 주 시작일(월요일, YYYY-MM-DD), B: 금요일 예상 출근(HH:MM) | 주별 금요일 예상 출근 저장 |

### 중복 처리
- 같은 날짜 데이터가 여러 행 존재하면 **마지막 행 기준** 사용 (`buildLastMap`)
- 퇴근 기록 시 A열에서 오늘 날짜를 역방향 탐색 후 C열 업데이트

---

## 5. 인증 (Google OAuth2 PKCE)

### 플로우
1. `getAuthToken()` 호출
2. 캐시된 `access_token`이 있고 만료 1분 이상 남은 경우 → 그대로 사용
3. `refresh_token`이 있으면 갱신 시도
4. 갱신 실패 또는 토큰 없음 → `startAuthFlow()` (팝업 인증창)

### PKCE 방식
- `code_verifier`: 32바이트 랜덤 → Base64URL
- `code_challenge`: SHA-256(code_verifier) → Base64URL
- `redirect_uri`: `https://{chrome.runtime.id}.chromiumapp.org/`
- scope: `https://www.googleapis.com/auth/spreadsheets`

### 설정 필수값
- Client ID (필수)
- Client Secret (웹 애플리케이션 유형 선택 시 필수)
- Redirect URI를 Google Cloud Console에 등록 필요

---

## 6. 출퇴근 기록 로직 (content.js)

### 감지 방식
- `document.addEventListener('click', handler, true)` — **capture phase** 사용
  - React 이벤트 핸들러보다 먼저 실행됨
  - MutationObserver 대신 이벤트 위임 사용 (React 렌더링 타이밍 문제 없음)

### 감지 조건 (모두 충족 시)
1. 클릭 대상이 `.OBTButton_themeblue__3JTE9` 클래스를 포함
2. 버튼 내 텍스트가 `확인`
3. `.OBTConfirm_confirmBoxStyle__3aqwI` 다이얼로그 안에 위치
4. 다이얼로그 메시지에 `출근 체크` 또는 `퇴근 체크` 포함

### 기록 시점
- 클릭 감지 즉시 `new Date()`로 날짜/시간 캡처
- `YYYY-MM-DD`, `HH:MM` 형식으로 background.js에 전달

---

## 7. 근무시간 계산 규칙

### 총체류시간 (gross)
```
gross = 퇴근시간 - 출근시간 (분 단위 계산, 시간 단위 반환)
```

### 순근무시간 (net) — 근로기준법 제54조 적용
```
gross < 4h  → net = gross (휴게 없음)
gross >= 4h → net = gross - 0.5h (30분 공제)
gross >= 8h → net = gross - 1h (1시간 공제)
```

### 특수 처리
| 상태 | netHours |
|---|---|
| 공휴일 | 8h (고정) |
| 연차 | 8h (고정) |
| 반차 | 실제 근무 net + 4h |
| 일반 근무 중 | gross → applyBreak(gross) |

### 주간 집계 (weeklyHours)
- 월~금 5일 기준
- **미래 날짜**: 공휴일/연차/반차만 포함, 실 근무 기록 없으면 0h
- 오늘 날짜가 포함된 미래 이전 날짜는 모두 집계

---

## 8. 팝업 UI 구성

### 레이아웃
```
[헤더: 제목 | 새로고침 ⟳ | 설정 ⚙ | 닫기 ✕]
[오늘 카드]
[이번 주 누적 카드]
[금요일 예상 퇴근 카드]
```

### 8-1. 오늘 카드

**표시 정보**
- 날짜 (YYYY-MM-DD + 한국어 요일: 월요일 ~ 일요일)
- 배지: 공휴일(빨강) / 연차(파랑) / 반차(초록)
- 시간 그리드: 출근 | 순근무 | 퇴근 (3등분)

**상태별 표시**
| 상태 | 출근 | 순근무 | 퇴근 |
|---|---|---|---|
| 미기록 | – | – | – |
| 근무 중 | HH:MM | 실시간 (id=`live-net`) | 근무중 (파랑) |
| 퇴근 완료 | HH:MM | net | HH:MM |
| 연차 | – | 연차 (8h 인정) | – |
| 공휴일 | – | 공휴일 — {이름} | – |
| 반차 | HH:MM | net + 반차 4h | HH:MM 또는 근무중 |

### 8-2. 주간 카드

**헤더**
- 섹션 제목: "이번 주 누적"
- 우측: `+ 휴가` 버튼 + `X.Xh / 40h` 요약

**진행 바** (`progress-fill`)
- 색상: 기본(파랑-청록) → 90% 이상(주황-빨강) → 100% 이상(초록)
- 너비: `Math.min(weeklyHours / 40 * 100, 100)%`
- transition: 0.4s ease

**일별 행** (`day-row`)
- 컬럼: 요일(한글 1자) | 출퇴근 시간 | 근무시간
- 배경색: 오늘(연파랑) / 공휴일(연분홍) / 연차(연파랑) / 반차(연초록) / 미래(opacity 0.45)
- 클릭 시 인라인 수정 폼 토글 (같은 행 재클릭 시 닫힘)
- 실시간 업데이트 대상: 오늘 근무 중인 행의 시간 (id=`live-day-hours`)

**빠른 휴가 추가 인라인 폼**
- `+ 휴가` 버튼 클릭 시 토글
- 날짜(date input) + 종류(연차 8h / 반차 4h) + 추가 버튼
- 기본값: 오늘 날짜
- 성공 시 2초 후 폼 숨김 + 대시보드 새로고침

**날짜 행 수정 폼**
- 행 클릭 시 출근/퇴근 시간 인라인 수정 가능
- HH:MM 형식 자동 완성 (숫자 2자리 입력 시 콜론 자동 삽입)
- 저장 시 Sheets API 업데이트 후 대시보드 새로고침

### 8-3. 금요일 예상 퇴근 카드

> **목적**: 주 40시간 달성을 위해 금요일에 몇 시간 근무해야 하는지 계산

#### 설계 원칙

**오늘이 월~목이고 아직 근무 중일 때**:
- 현재 실시간 업무시간이 **8h 미만**이면 → 오늘 8h 근무로 가정 (안정적 예측)
- 현재 실시간 업무시간이 **8h 이상**이면 → 실제 시간 그대로 반영 (야근 반영)

**오늘 퇴근 완료 후**: 확정된 실제 net 사용 (8h 미달이어도 그 시간이 오늘 업무시간)

**근거**: 8h 채우기 전에는 "오늘은 8h 채울 것"으로 가정해야 금요일 예상이 안정적.
야근 시에는 이미 초과했으므로 실제 시간을 반영해야 금요일이 정확히 줄어듦.

#### 금요일 필요 근무시간 계산

**오늘 유효 업무시간 (todayEffective)**:
```
월~목 근무 중 + todayNet < 8h  → todayEffective = 8h (안정 예측)
월~목 근무 중 + todayNet >= 8h → todayEffective = todayNet (야근 반영)
월~목 퇴근 완료                → todayEffective = today.netHours (확정값)
금요일 (근무 중/완료 무관)     → todayEffective = 0 (금요일 자신은 제외, 별도 계산)
```

**금요일 근무 중 예상 퇴근 계산**:
- `fridayRemaining = MAX(0, 40 - weeklyHours_월목실적)` (금요일 자신 제외)
- 출근 시간이 찍히면 해당 시간을 checkin 필드에 자동 동기화
- `예상 퇴근 = 실제 출근 시간 + netToGross(fridayRemaining)`


**핵심 공식**:
```
fridayRemaining = MAX(0, 40 - weeklyExcludingToday - todayEffective - plannedAfterToday)
```
> `weeklyExcludingToday`: 오늘 미퇴근 시 today.netHours=0이므로 weeklyHours 그대로.
> 퇴근 완료 시 weeklyHours에 이미 포함되어 있으므로 todayEffective = today.netHours.

**plannedAfterToday 계산** (오늘 다음날 ~ 목요일):
```
각 날짜별:
  공휴일 또는 연차 → 0h (이미 weeklyHours에 포함됨)
  반차             → 4h
  일반             → 8h
```

**요일별 동작**:
| 오늘 | todayEffective | 계획 공제 대상 |
|---|---|---|
| 월요일 (근무 중, 2h) | 8h | 화(8), 수(8), 목(8) |
| 월요일 (근무 중, 9h) | 9h | 화(8), 수(8), 목(8) |
| 월요일 (퇴근 완료, 6h) | 6h | 화(8), 수(8), 목(8) |
| 월요일 (퇴근 완료, 10h) | 10h | 화(8), 수(8), 목(8) |
| 화요일 (근무 중) | 8h or 실제 | 수(8), 목(8) |
| 수요일 (근무 중) | 8h or 실제 | 목(8) |
| 목요일 (근무 중) | 8h or 실제 | 없음 |
| 금요일 (출근 전) | 0h (제외, 월~목 실적으로만 계산) | 없음 |
| 금요일 (근무 중) | 0h (제외, 출근 시간 동기화 후 예상 퇴근 표시) | 없음 |

#### 하루 필요 근무시간 → 예상 퇴근 계산

```
dailyNet   = 반차면 4h, 아니면 MIN(8, fridayRemaining)
dailyGross = netToGross(dailyNet)
예상 퇴근  = 출근시간 + dailyGross * 60분
```

**netToGross 역산** (휴게시간 포함, P1-P5 역함수):
```
net <= 0  → gross = 0
net > 8   → gross = net + 1   (P5 구간: gross > 9h)
net > 4   → gross = net + 0.5 (P3 구간: gross 4.5h~8.5h)
그 외      → gross = net       (P1 구간: gross ≤ 4h)
```

#### 금요일 출근 시간 동기화

- **금요일 출근 전**: WeeklySettings에 저장된 예상 출근 시간으로 계산 (기본값 09:00)
- **금요일 출근 기록 생성 시**: Sheets의 실제 출근 시간을 입력 필드에 자동 동기화 → 예상 퇴근 재계산
- 출근 시간 입력 필드에서 수동 수정 시 → 1.5초 디바운스 후 WeeklySettings에 저장 → 해당 주 내내 적용

**출근 시간 우선순위**:
1. 실제 금요일 출근 기록 (Sheets 데이터)
2. WeeklySettings에 저장된 예상 출근 시간
3. 기본값: `09:00`

#### 특수 상태 표시
| 상태 | 표시 |
|---|---|
| 주 40h 달성 | "이번 주 목표 달성!" + 초과시간 |
| 금요일 연차 | "금요일 연차" + 주간 누적 + 남은시간 |
| 예상 퇴근 22시 이상 | "야근 구간" (주황) |
| 예상 퇴근 24시 이상 | "자정을 넘어갑니다" (빨강) |

#### 예시 시나리오
```
[월요일 오전 10시, 현재 2h 근무 중]
  weeklyExcludingToday = 0h
  todayEffective       = 8h (2h < 8h → 8h 가정)
  plannedAfterToday    = 화(8) + 수(8) + 목(8) = 24h
  fridayRemaining      = 40 - 0 - 8 - 24 = 8h
  → 금요일 8h 풀근무 예정 (09:00 출근 기준 → 18:00 퇴근)

[월요일 오후 늦게, 현재 9h 근무 중 (야근)]
  weeklyExcludingToday = 0h
  todayEffective       = 9h (9h >= 8h → 실제 반영)
  plannedAfterToday    = 화(8) + 수(8) + 목(8) = 24h
  fridayRemaining      = 40 - 0 - 9 - 24 = 7h
  → 금요일 7h 근무 예정 (09:00 출근 기준 → 16:30 퇴근)

[월요일 6h 퇴근 완료 (조기 퇴근)]
  weeklyHours          = 6h (확정)
  todayEffective       = 6h (퇴근 완료 → 실제값)
  plannedAfterToday    = 화(8) + 수(8) + 목(8) = 24h
  fridayRemaining      = 40 - 6 - 24 = 10h → MIN(8, 10) = 8h
  → 금요일 8h 풀근무 예정

[금요일 09:10 출근]
  weeklyHours(월~목)   = 34h (예시)
  fridayRemaining      = 40 - 34 = 6h
  출근 시간 09:10 자동 동기화
  → 예상 퇴근 = 09:10 + 6.5h = 15:40
```

---

## 9. 실시간 업데이트

### 조건
- 오늘 `startTime`이 있고 `endTime`이 없으며, 공휴일/연차가 아닌 경우
- **비활성화 조건**: 퇴근 완료, 공휴일, 연차, 오늘 출근 기록 없음

### 동작
- `startLiveUpdates()` 호출 시 즉시 1회 실행 후 60초 인터벌 반복
- 팝업 새로고침(`loadDashboard`) 시 기존 인터벌 초기화 후 재시작

### `liveUpdateAll()` 업데이트 대상
1. **오늘 카드** 순근무 (`id="live-net"`)
2. **주간 카드** 오늘 행 시간 (`id="live-day-hours"`)
3. **주간 카드** 진행 바 + 누적 요약 (`weekly-summary`, `progress-fill`)
4. **금요일 카드** 요약 (`fri-summary`)
5. **금요일 카드** 예상 퇴근 시간 (`friday-checkout`)

### 실시간 주간 합계 계산
```
liveWeekly = baseWeekly - today.netHours(저장값) + todayNet(실시간)
```
> `baseWeekly`는 dashboardData 로드 시점의 주간 합계.
> 오늘 저장된 값을 실시간 값으로 교체하여 계산.

---

## 10. 캐시 전략

| 동작 | 캐시 처리 |
|---|---|
| 팝업 열기 (일반) | 캐시 있으면 사용 (TTL: 5분) |
| 팝업 새로고침 버튼 | `dashboardCache` 삭제 후 재조회 |
| 출퇴근 기록 성공 | `dashboardCache` 삭제 |
| 출퇴근 수정 성공 | `dashboardCache` 삭제 |
| 휴가 추가 성공 | `dashboardCache` 삭제 |
| 설정 저장 | `dashboardCache` 삭제 |

---

## 11. 오류 처리

### 오류 화면 표시 조건
- 메시지에 `Client ID` 또는 `설정` 포함 → "설정 열기" 버튼 표시
- 그 외 → "다시 시도" 버튼 표시

### 주요 오류 케이스
| 오류 | 원인 | 조치 |
|---|---|---|
| Client ID가 설정되지 않았습니다 | options.html에서 미설정 | 설정 페이지 이동 |
| Spreadsheet ID가 설정되지 않았습니다 | options.html에서 미설정 | 설정 페이지 이동 |
| 인증이 취소되었습니다 | 팝업창 닫음 | 재시도 |
| 토큰 갱신 실패 | refresh_token 만료 | 재인증 진행 |

---

## 12. 설정 페이지 (options.html)

### 입력 항목
| 항목 | 필수 | 설명 |
|---|---|---|
| Client ID | 필수 | Google Cloud Console OAuth 클라이언트 ID |
| Client Secret | 선택 | 웹 애플리케이션 유형 사용 시 필요 |
| Spreadsheet ID | 필수 | 시트 URL의 `/d/`와 `/edit` 사이 값 |
| 출퇴근 시트 이름 | 선택 | 기본값: `출퇴근 기록부` |

### Redirect URI
- 자동 계산: `https://{chrome.runtime.id}.chromiumapp.org/`
- 복사 버튼으로 클립보드 복사 가능
- Google Cloud Console 승인된 리디렉션 URI에 등록 필요

### 버튼
- **설정 저장**: `chrome.storage.sync`에 저장 + 캐시 초기화
- **Google 인증**: `getDashboardData` 호출 → 인증 플로우 트리거
- **로그아웃**: `auth` + `dashboardCache` 삭제

---

## 13. 배포 방법

### 설치 (최초)
1. 알집 해제
2. Chrome → `chrome://extensions` → 개발자 모드 ON
3. "압축 해제된 확장 프로그램 로드" → 폴더 선택
4. 설정 페이지에서 Client ID, Spreadsheet ID 입력 후 저장
5. "Google 인증" 버튼으로 최초 인증

### 업데이트 (기존 사용자)
- 기존 폴더에 파일 덮어씌우기
- Chrome 확장 관리자에서 새로고침(↺) 버튼 클릭
- **사용자 데이터(설정, 인증 토큰) 유지됨** — chrome.storage는 파일과 분리된 저장소

---

## 14. 알려진 제약사항 / 주의사항

- `chrome.action.openPopup()`: Chrome 127+ 에서만 동작, 이하 버전은 무시
- 같은 날짜 중복 출근 기록 시 마지막 행 기준 사용
- 출퇴근 기록 없이 퇴근 기록 시도 시 빈 출근 행을 생성 후 퇴근 시간 추가
- 금요일 예상 퇴근 카드는 월~목 근무 중일 때만 실시간 업데이트됨
- WeeklySettings 저장은 주 월요일 날짜를 키로 사용
- 반차이면서 근무 기록이 있는 날의 netHours = 실근무 net + 4h (중복 아님)
