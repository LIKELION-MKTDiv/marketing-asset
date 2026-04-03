# CHANGELOG

> 커밋할 때마다 자동 기록. 최신순 정렬.

---

## 2026-04-02 | 오늘
**feat: 마지막 근무일 동적 탐색 + P1-P5 휴게시간 + todayEffective 로직**
- `lastWorkDayIndex`: 금요일부터 역순으로 탐색, 공휴일/연차 건너뜀 → 마지막 실 근무일 동적 결정
  - 금요일 연차/공휴일 → 목요일 예상 퇴근으로 카드 전환
  - 목+금 연차/공휴일 → 수요일 예상 퇴근으로 카드 전환 (최대 월요일까지)
  - 주간 전체 연차/공휴일 → "이번 주 전체 연차/공휴일" 메시지 표시
- `todayEffective`: 근무 중 todayNet < 8h → 8h 가정, todayNet ≥ 8h → 실제 반영, 퇴근 완료 → 확정값
- `plannedHours`: 오늘+1 ~ 마지막근무일-1 사이 날들의 계획 근무시간 합산 (공휴일 0h, 반차 4h, 일반 8h)
- `applyBreak(gross)` P1-P5 구역 재설계 (역전 현상 방지):
  - P1: ≤4h → 휴게 없음 / P2: 4~4.5h → 4h 상한 / P3: 4.5~8.5h → -30분
  - P4: 8.5~9h → 8h 상한 / P5: >9h → -1시간
- `netToGross(net)`: P1-P5에 맞게 역산 함수 업데이트
- popup.html: `<span id="last-day-title">` 추가 → 카드 제목 동적 변경 지원
- **docs: PRD.md 동적 마지막 근무일 + P1-P5 + todayEffective 섹션 반영**
- **docs: PRD.md 불필요한 코멘트 라인 제거**

---

## 2026-04-01
**fix: 금요일 예상 퇴근 실시간 반영 버그 수정 + 계획 근무시간 공제 로직 추가**
**fix: 금요일 예상 퇴근 실시간 반영 버그 수정 + 계획 근무시간 공제 로직 추가**
- `liveUpdateAll`: `fridayRemaining` 계산에서 `+ todayNet` 중복 합산 제거
- 화수목 계획 근무시간(8h × N일)을 금요일 필요 근무시간에서 공제
  - 오늘 다음날 ~ 목요일 사이를 대상으로 `plannedHours` 계산
  - 공휴일/연차 → 0h, 반차 → 4h, 일반 → 8h
- `renderFriday` + `liveUpdateAll` 두 곳 모두 동일 로직 적용
- **docs: PRD.md 초안 작성** — 전체 동작 명세 문서화
- **docs: CHANGELOG.md 생성**

---

## 이전 히스토리 (요약)

| 커밋 | 내용 |
|------|------|
| `277b3aa` | Amaranth 출퇴근 체크 확장프로그램 추가 및 설치 마법사 개선 |
| `d9d79ed` | Amaranth 설치 마법사 설정 안내 개선 |
| `d344d5a` | Amaranth 출퇴근 체크 확장프로그램 추가 |
