/**
 * 설문 응답 2개 시트 합산 → 슬랙 알림
 *
 * 설치 방법 (두 스프레드시트 모두에 동일하게 반복):
 * 1. 각 응답 스프레드시트 열기 → 확장 프로그램 → Apps Script
 * 2. 기본 코드 지우고 이 파일 내용 전체 붙여넣기
 * 3. 아래 SHEET_A_ID / SHEET_B_ID / SLACK_WEBHOOK_URL을 실제 값으로 채워넣기
 * 4. 좌측 시계 아이콘(트리거) → 트리거 추가
 *    - 실행할 함수: checkAndAlert
 *    - 이벤트 소스: 스프레드시트에서
 *    - 이벤트 유형: 양식 제출 시 (onFormSubmit)
 *    - 저장 → 최초 1회 권한 승인 필요
 * 5. 두 스프레드시트 모두 같은 방식으로 설치 (총 2번)
 *
 * 응답이 들어올 때마다 두 시트 합산 건수를 슬랙으로 보내고,
 * 지정한 목표 건수(LIMIT)에 도달/초과하면 중단 안내 문구를 추가로 붙입니다.
 */

const SHEET_A_ID = "YOUR_SHEET_A_ID"; // 첫 번째 응답 시트(예: 재구매 설문)
const SHEET_A_GID = 0;
const SHEET_B_ID = "YOUR_SHEET_B_ID"; // 두 번째 응답 시트(예: 신규구매 설문)
const SHEET_B_GID = 0;
const SLACK_WEBHOOK_URL = "YOUR_SLACK_WEBHOOK_URL"; // Slack Incoming Webhook URL
const LIMIT = 50; // 목표 응답 건수

function countResponses(spreadsheetId, gid) {
  const ss = SpreadsheetApp.openById(spreadsheetId);
  const sheets = ss.getSheets();
  const target = sheets.find(s => s.getSheetId() === gid) || sheets[0];
  const lastRow = target.getLastRow();
  return Math.max(0, lastRow - 1); // 헤더 행 제외
}

function checkAndAlert() {
  const countA = countResponses(SHEET_A_ID, SHEET_A_GID);
  const countB = countResponses(SHEET_B_ID, SHEET_B_GID);
  const total = countA + countB;

  const now = new Date();
  const tz = Session.getScriptTimeZone();
  const label = Utilities.formatDate(now, tz, "M월 d일 H시");

  let text = `📊 설문 응답 현황 — ${label} 기준 총 ${total}건 (시트A ${countA}건 + 시트B ${countB}건)`;

  if (total >= LIMIT) {
    text += `\n🚨 ${LIMIT}건 도달 — 응답 중단이 필요합니다.`;
  }

  UrlFetchApp.fetch(SLACK_WEBHOOK_URL, {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ text }),
  });
}
