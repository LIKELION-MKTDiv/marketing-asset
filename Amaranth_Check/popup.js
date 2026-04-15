'use strict';

const DAY_KO   = ['일', '월', '화', '수', '목', '금', '토'];
const DAY_FULL = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
let liveTimerID    = null;
let fridaySaveTimer = null;
let dashboardData  = null; // 실시간 업데이트용 전역 캐시

// ── 초기화 ──────────────────────────────────────────────────────────────────

document.getElementById('btn-settings').addEventListener('click', () => chrome.runtime.openOptionsPage());
document.getElementById('btn-close').addEventListener('click', () => window.close());
document.getElementById('btn-refresh').addEventListener('click', () => loadDashboard(true));

// 날짜 행 클릭 → 수정 폼
document.getElementById('day-list').addEventListener('click', (e) => {
  if (e.target.closest('.edit-panel')) return; // 폼 내부 클릭 무시
  const row = e.target.closest('.day-row');
  if (!row || !row.dataset.date) return;

  // 이미 열린 폼 닫기
  const existing = document.querySelector('.edit-panel');
  const wasThis = existing && existing.previousElementSibling === row;
  document.querySelectorAll('.edit-panel').forEach(p => p.remove());
  document.querySelectorAll('.day-row.editing').forEach(r => r.classList.remove('editing'));
  if (wasThis) return; // 같은 행 재클릭 시 토글 닫기

  row.classList.add('editing');
  const panel = document.createElement('div');
  panel.className = 'edit-panel';
  panel.innerHTML = `
    <div class="edit-row">
      <span class="edit-label">출근</span>
      <input type="text" id="edit-start" placeholder="HH:MM" maxlength="5" value="${row.dataset.start || ''}" class="edit-time-input" />
    </div>
    <div class="edit-row">
      <span class="edit-label">퇴근</span>
      <input type="text" id="edit-end" placeholder="HH:MM" maxlength="5" value="${row.dataset.end || ''}" class="edit-time-input" />
    </div>
    <div class="edit-actions">
      <button class="edit-btn-save">저장</button>
      <button class="edit-btn-cancel">취소</button>
    </div>
    <div class="edit-msg" id="edit-msg"></div>
  `;
  row.insertAdjacentElement('afterend', panel);

  // HH:MM 자동 포맷
  panel.querySelectorAll('.edit-time-input').forEach(inp => {
    inp.addEventListener('input', e => {
      let v = e.target.value.replace(/[^0-9:]/g, '');
      if (v.length === 2 && !v.includes(':') && e.inputType !== 'deleteContentBackward') v = v + ':';
      if (v.length > 5) v = v.slice(0, 5);
      e.target.value = v;
      const valid = /^([01]\d|2[0-3]):([0-5]\d)$/.test(v);
      e.target.style.borderColor = valid ? '' : '#e53935';
    });
  });

  panel.querySelector('.edit-btn-cancel').addEventListener('click', () => {
    panel.remove();
    row.classList.remove('editing');
  });

  panel.querySelector('.edit-btn-save').addEventListener('click', () => {
    const startTime = document.getElementById('edit-start').value;
    const endTime   = document.getElementById('edit-end').value;
    const msgEl     = document.getElementById('edit-msg');
    if (!startTime) { msgEl.textContent = '출근 시간을 입력하세요'; return; }
    if (!/^([01]\d|2[0-3]):([0-5]\d)$/.test(startTime)) { msgEl.textContent = '올바른 시간 형식으로 입력하세요 (예: 09:00)'; return; }
    if (endTime && !/^([01]\d|2[0-3]):([0-5]\d)$/.test(endTime)) { msgEl.textContent = '퇴근 시간 형식을 확인하세요 (예: 18:30)'; return; }
    msgEl.textContent = '저장 중...';
    chrome.runtime.sendMessage(
      { action: 'updateAttendance', date: row.dataset.date, startTime, endTime },
      (response) => {
        if (chrome.runtime.lastError || !response?.success) {
          msgEl.textContent = response?.error || '저장 실패';
          return;
        }
        panel.remove();
        row.classList.remove('editing');
        loadDashboard(true);
      }
    );
  });
});
// 빠른 휴가 추가 (주간 카드 헤더 버튼)
document.getElementById('btn-leave-quick').addEventListener('click', () => {
  const form = document.getElementById('quick-leave-form');
  form.style.display = form.style.display === 'none' ? 'flex' : 'none';
});
document.getElementById('ql-submit').addEventListener('click', onQuickLeave);

// 오늘 날짜를 ql-date 기본값으로
document.getElementById('ql-date').value = todayStr();

loadDashboard(false);

// ── 대시보드 로드 ────────────────────────────────────────────────────────────

function loadDashboard(forceRefresh) {
  if (forceRefresh) {
    // 캐시 무효화 후 재조회
    chrome.storage.local.remove(['dashboardCache'], () => fetchDashboard());
  } else {
    fetchDashboard();
  }
}

function fetchDashboard() {
  chrome.runtime.sendMessage({ action: 'getDashboardData' }, (response) => {
    if (chrome.runtime.lastError) {
      renderError(chrome.runtime.lastError.message);
      return;
    }
    if (!response?.success) {
      renderError(response?.error || '데이터 조회 실패');
      return;
    }
    renderDashboard(response.data);
  });
}

// ── 렌더링 ──────────────────────────────────────────────────────────────────

function renderDashboard(data) {
  dashboardData = data;
  const { days, weeklyHours, weekDates, assumedFridayStart } = data;
  const today = days.find(d => d.isToday);

  renderToday(today);
  renderWeekly(days, weeklyHours);
  renderFriday(days, weeklyHours, weekDates[0], assumedFridayStart);
  startLiveUpdates();
}

// ─ 오늘 카드 ────────────────────────────────────────────────────────────────

function renderToday(day) {
  if (liveTimerID) { clearInterval(liveTimerID); liveTimerID = null; }

  const body = document.getElementById('today-body');
  if (!day) { body.innerHTML = '<div class="today-no-record">오늘 데이터 없음</div>'; return; }

  const now  = new Date();
  const dow  = DAY_FULL[now.getDay()];
  const dateLabel = `${day.date} (${dow})`;

  // 배지
  let badge = '';
  if (day.isHoliday) {
    badge = `<span class="badge badge-holiday">${day.holidayName}</span>`;
  } else if (day.leaveType === '연차') {
    badge = `<span class="badge badge-leave">연차</span>`;
  } else if (day.leaveType === '반차') {
    badge = `<span class="badge badge-halfleave">반차</span>`;
  }

  const isWorking = day.startTime && !day.endTime && !day.isHoliday && day.leaveType !== '연차';

  body.innerHTML = `
    <div class="today-row">
      <span class="today-date">${dateLabel}</span>
      ${badge}
    </div>
    ${buildTimeGrid(day, isWorking)}
  `;

}

function buildTimeGrid(day, isWorking) {
  if (day.isHoliday) {
    return `<div class="today-no-record" style="color:#e57373">공휴일 — ${day.holidayName}</div>`;
  }
  if (day.leaveType === '연차') {
    return `<div class="today-no-record" style="color:#1565c0">연차 (8h 인정)</div>`;
  }

  const startVal = day.startTime ? `<span class="value">${padTime(day.startTime)}</span>`
                                 : `<span class="value muted">–</span>`;
  const endVal   = day.endTime   ? `<span class="value">${padTime(day.endTime)}</span>`
                 : isWorking     ? `<span class="value" style="color:#fb8c00">근무중</span>`
                                 : `<span class="value muted">–</span>`;

  // 실시간 순근무
  let netVal = '';
  if (day.startTime) {
    const endT  = day.endTime ? day.endTime : formatTime(new Date());
    const gross = calcGrossHours(day.startTime, endT);
    const net   = applyBreak(gross);
    const extra = day.leaveType === '반차' ? 4 : 0;
    netVal = `<span class="value${isWorking ? '' : ''}" id="live-net">${fmtHours(net + extra)}</span>`;
    if (day.leaveType === '반차') {
      netVal += `<div style="font-size:10px;color:#66bb6a;margin-top:2px">+반차 4h</div>`;
    }
  } else {
    netVal = `<span class="value muted">–</span>`;
  }

  return `
    <div class="time-grid">
      <div class="time-box">
        <div class="label">출근</div>
        ${startVal}
      </div>
      <div class="time-box">
        <div class="label">순근무</div>
        ${netVal}
      </div>
      <div class="time-box${isWorking ? ' working' : ''}">
        <div class="label">퇴근</div>
        ${endVal}
      </div>
    </div>
  `;
}

// ─ 주간 카드 ─────────────────────────────────────────────────────────────────

function renderWeekly(days, weeklyHours) {
  const TARGET   = 40;
  const pct      = Math.min((weeklyHours / TARGET) * 100, 100);
  const fillEl   = document.getElementById('progress-fill');
  const summaryEl= document.getElementById('weekly-summary');

  summaryEl.textContent = `${fmtHours(weeklyHours)} / ${TARGET}h`;
  fillEl.style.width = `${pct}%`;
  fillEl.className = 'progress-fill' +
    (weeklyHours >= TARGET ? ' over' : weeklyHours >= TARGET * 0.9 ? ' warn' : '');

  const list = document.getElementById('day-list');
  list.innerHTML = days.map(d => buildDayRow(d)).join('');
}

function buildDayRow(d) {
  const dayDate = new Date(d.date + 'T00:00:00');
  const dayName = DAY_KO[dayDate.getDay()];

  let rowClass = 'day-row';
  if (d.isToday)          rowClass += ' today-row-item';
  if (d.isHoliday)        rowClass += ' holiday';
  else if (d.leaveType === '연차') rowClass += ' leave';
  else if (d.leaveType === '반차') rowClass += ' halfleave';
  if (d.isFuture)         rowClass += ' future';

  let timesHtml = '';
  let hoursClass = 'day-hours';

  if (d.isHoliday) {
    timesHtml = `<span class="em">📅 ${d.holidayName}</span>`;
    hoursClass += ' h-holiday';
  } else if (d.leaveType === '연차') {
    timesHtml = `<span class="em">✈ 연차</span>`;
    hoursClass += ' h-leave';
  } else if (d.leaveType === '반차') {
    const t = d.startTime ? `${padTime(d.startTime)} → ${d.endTime ? padTime(d.endTime) : '근무중'}` : '';
    timesHtml = t ? `${t} · <span class="em">◑ 반차</span>` : `<span class="em">◑ 반차</span>`;
    hoursClass += ' h-halfleave';
  } else if (d.startTime) {
    const arrow = d.endTime ? `${padTime(d.startTime)} → ${padTime(d.endTime)}` : `${padTime(d.startTime)} → 근무중`;
    timesHtml = arrow;
    hoursClass += ' h-worked';
  } else if (d.isFuture) {
    timesHtml = '–';
    hoursClass += ' h-worked';
  } else {
    timesHtml = '<span style="color:#ccc">기록 없음</span>';
  }

  // 연차·반차·공휴일·출퇴근 기록이 있으면 시간 표시 (미래 예정 연차도 포함)
  const hasRecord = d.isHoliday || d.leaveType || d.startTime;
  const hoursHtml = hasRecord ? fmtHoursHtml(d.netHours) : '–';
  // 오늘 근무 중이면 id 부여 → liveUpdateAll에서 실시간 업데이트
  const hoursId = (d.isToday && d.startTime && !d.endTime) ? ' id="live-day-hours"' : '';

  return `
    <div class="${rowClass}" data-date="${d.date}" data-start="${padTime(d.startTime)}" data-end="${padTime(d.endTime)}" style="cursor:pointer">
      <span class="day-name">${dayName}</span>
      <span class="day-times">${timesHtml}</span>
      <span class="${hoursClass}"${hoursId}>${hoursHtml}</span>
    </div>
  `;
}

// ─ 금요일 예상 퇴근 카드 ─────────────────────────────────────────────────────

function renderFriday(days, weeklyHours, weekId, assumedFridayStart) {
  const body = document.getElementById('friday-body');
  if (!body) return;

  const TARGET     = 40;
  const todayIndex = days.findIndex(d => d.isToday);
  const today      = todayIndex >= 0 ? days[todayIndex] : null;

  // 마지막 근무 예정일 탐색 (금요일부터 역순, 연차/공휴일 제외)
  let lastWorkDayIndex = -1;
  for (let i = 4; i >= 0; i--) {
    if (!days[i].isHoliday && days[i].leaveType !== '연차') {
      lastWorkDayIndex = i;
      break;
    }
  }

  // 이번 주 전체 연차/공휴일
  if (lastWorkDayIndex === -1) {
    body.innerHTML = `<div class="fri-done">이번 주 전체 연차/공휴일</div>`;
    return;
  }

  const targetDay = days[lastWorkDayIndex];

  // 카드 제목 동적 업데이트 (yyyy-mm-dd 주차 O요일 예상 퇴근)
  const titleEl = document.getElementById('last-day-title');
  if (titleEl) titleEl.textContent = `${weekId} 주차 ${DAY_FULL[new Date(targetDay.date + 'T00:00:00').getDay()]} 예상 퇴근`;

  // 오늘 유효 업무시간: 마지막 근무일 이전인 정상 근무일이면 8h 가정 (출근 전/근무 중 모두 포함)
  const todayEffective = (today && !today.isHoliday && today.leaveType !== '연차' && !today.endTime && todayIndex < lastWorkDayIndex)
    ? (today.leaveType === '반차' ? 4 : 8)
    : 0;

  // 오늘 이후 ~ 마지막 근무일 직전까지 계획 근무시간 (연차/공휴일 제외)
  const plannedHours = (todayIndex >= 0 && todayIndex < lastWorkDayIndex)
    ? days.slice(todayIndex + 1, lastWorkDayIndex).reduce((sum, d) => {
        if (d.isHoliday || d.leaveType === '연차') return sum;
        return sum + (d.leaveType === '반차' ? 4 : 8);
      }, 0)
    : 0;

  const remaining = Math.max(0, TARGET - weeklyHours - todayEffective - plannedHours);

  // 목표 달성
  if (weeklyHours >= TARGET) {
    body.innerHTML = `
      <div class="fri-done">이번 주 목표 달성!</div>
      <div class="fri-done-sub">주간 누적 ${fmtHours(weeklyHours)} · +${fmtHours(weeklyHours - TARGET)} 초과</div>
    `;
    return;
  }

  // 하루 기준 gross: 반차면 4h, 아니면 실제 남은 시간 그대로 반영
  const dailyNet   = targetDay.leaveType === '반차' ? 4 : remaining;
  const dailyGross = netToGross(dailyNet);
  const dailyLabel = targetDay.leaveType === '반차' ? '하루 4h 기준 (반차)'
                   : `남은 ${fmtHours(remaining)} 기준`;
  const dayLabel   = DAY_FULL[new Date(targetDay.date + 'T00:00:00').getDay()];

  // 실제 출근 기록 > WeeklySettings(금요일만) > 기본값 09:00
  const assumedStart = lastWorkDayIndex === 4 ? assumedFridayStart : '';
  const prefill = padTime(targetDay.startTime || assumedStart) || '09:00';

  const weekRemaining = Math.max(0, TARGET - weeklyHours - todayEffective);
  body.innerHTML = `
    <div class="fri-summary" id="fri-summary">
      주간 누적 <span class="em">${fmtHours(weeklyHours + todayEffective)}</span><span class="sep">|</span>남은 시간 <span class="em">${fmtHours(weekRemaining)}</span>
    </div>
    <div class="fri-calc">
      <div class="fri-row">
        <span class="label">${dayLabel} 출근</span>
        <input type="text" id="friday-checkin" placeholder="09:00" maxlength="5" value="${prefill}" class="fri-time-input" />
      </div>
      <div class="fri-row" style="margin-top:2px">
        <span class="label">예상 퇴근 <span class="fri-basis">${dailyLabel}</span></span>
        <span class="fri-result" id="friday-checkout">–</span>
      </div>
      <div class="fri-note" id="friday-note"></div>
    </div>
  `;

  const input = document.getElementById('friday-checkin');

  // HH:MM 자동 포맷 (숫자 입력 시 콜론 자동 삽입)
  input.addEventListener('input', e => {
    let v = e.target.value.replace(/[^0-9:]/g, '');
    if (v.length === 2 && !v.includes(':') && e.inputType !== 'deleteContentBackward') {
      v = v + ':';
    }
    if (v.length > 5) v = v.slice(0, 5);
    e.target.value = v;

    const valid = /^([01]\d|2[0-3]):([0-5]\d)$/.test(v);
    e.target.style.borderColor = valid ? '' : '#e53935';
    if (!valid) return;

    updateFridayCheckout(v, dailyGross);
    clearTimeout(fridaySaveTimer);
    // WeeklySettings 저장은 마지막 근무일이 금요일인 경우만
    if (weekId && lastWorkDayIndex === 4) {
      fridaySaveTimer = setTimeout(() => {
        chrome.runtime.sendMessage({ action: 'saveWeekSetting', weekId, assumedStartTime: v });
      }, 1500);
    }
  });
  if (prefill) updateFridayCheckout(prefill, dailyGross);
}

// 출근 시간 + 필요 총근무시간 → 예상 퇴근 시간 계산
function updateFridayCheckout(checkinTime, grossHours) {
  const outEl  = document.getElementById('friday-checkout');
  const noteEl = document.getElementById('friday-note');
  if (!outEl || !checkinTime) return;

  const [h, m]   = checkinTime.split(':').map(Number);
  const endMin   = h * 60 + m + Math.round(grossHours * 60);
  const endH     = Math.floor(endMin / 60);
  const endM     = endMin % 60;
  const checkout = `${String(endH % 24).padStart(2,'0')}:${String(endM).padStart(2,'0')}`;

  outEl.textContent = checkout;

  if (noteEl) {
    if (endH >= 24) {
      noteEl.textContent = '자정을 넘어갑니다';
      noteEl.style.color = '#e53935';
    } else if (endH >= 22) {
      noteEl.textContent = '야근 구간';
      noteEl.style.color = '#fb8c00';
    } else {
      noteEl.textContent = '';
    }
  }
}

// 순근무시간(net) → 총체류시간(gross) 역산
function netToGross(net) {
  if (net <= 0)  return 0;
  if (net > 7.5) return net + 1;   // 8.5h 이상 체류 구간 역산: gross = net + 1h
  if (net > 4)   return net + 0.5; // 4.5h~8.5h 체류 구간 역산: gross = net + 0.5h
  return net;                       // 4h 이하: 공제 없음
}

// ─ 실시간 업데이트 ────────────────────────────────────────────────────────────

function startLiveUpdates() {
  if (liveTimerID) { clearInterval(liveTimerID); liveTimerID = null; }

  const today = dashboardData?.days?.find(d => d.isToday);
  const isWorking = today?.startTime && !today?.endTime
                 && !today?.isHoliday && today?.leaveType !== '연차';
  if (!isWorking) return;

  liveUpdateAll(); // 즉시 1회 실행
  liveTimerID = setInterval(liveUpdateAll, 60_000);
}

function liveUpdateAll() {
  if (!dashboardData) return;
  const { days, weeklyHours: baseWeekly } = dashboardData;
  const today = days.find(d => d.isToday);
  if (!today?.startTime || today.endTime) return;

  // 오늘 현재 순근무
  const gross   = calcGrossHours(today.startTime, formatTime(new Date()));
  const net     = applyBreak(gross);
  const extra   = today.leaveType === '반차' ? 4 : 0;
  const todayNet = Math.max(0, net + extra);

  // 오늘 카드 순근무 업데이트
  const netEl = document.getElementById('live-net');
  if (netEl) netEl.textContent = fmtHours(todayNet);

  // 주간 카드 오늘 행 시간 업데이트
  const dayHoursEl = document.getElementById('live-day-hours');
  if (dayHoursEl) dayHoursEl.innerHTML = fmtHoursHtml(todayNet);

  // 실시간 주간 합계 = 저장된 합계 - 오늘 저장값 + 오늘 현재값
  const liveWeekly = baseWeekly - today.netHours + todayNet;

  // 주간 카드 업데이트
  const TARGET = 40;
  const pct = Math.min((liveWeekly / TARGET) * 100, 100);
  const summaryEl = document.getElementById('weekly-summary');
  const fillEl    = document.getElementById('progress-fill');
  if (summaryEl) summaryEl.textContent = `${fmtHours(liveWeekly)} / ${TARGET}h`;
  if (fillEl) {
    fillEl.style.width = `${pct}%`;
    fillEl.className = 'progress-fill' +
      (liveWeekly >= TARGET ? ' over' : liveWeekly >= TARGET * 0.9 ? ' warn' : '');
  }

  // 마지막 근무 예정일 탐색 (금요일부터 역순, 연차/공휴일 제외)
  const todayIndex = days.findIndex(d => d.isToday);
  let lastWorkDayIndex = -1;
  for (let i = 4; i >= 0; i--) {
    if (!days[i].isHoliday && days[i].leaveType !== '연차') {
      lastWorkDayIndex = i;
      break;
    }
  }
  if (lastWorkDayIndex === -1) return; // 이번 주 전체 연차/공휴일

  const targetDay = days[lastWorkDayIndex];

  // 오늘 유효 업무시간: 마지막 근무일 이전이면 8h/실제 적용, 마지막 근무일 당일이면 0(자신 제외)
  const weeklyExcludingToday = baseWeekly - today.netHours;
  const todayEffective = (todayIndex < lastWorkDayIndex) ? (todayNet >= 8 ? todayNet : 8) : 0;

  const plannedHours = (todayIndex >= 0 && todayIndex < lastWorkDayIndex)
    ? days.slice(todayIndex + 1, lastWorkDayIndex).reduce((sum, d) => {
        if (d.isHoliday || d.leaveType === '연차') return sum;
        return sum + (d.leaveType === '반차' ? 4 : 8);
      }, 0)
    : 0;
  const fridayRemaining = Math.max(0, TARGET - weeklyExcludingToday - todayEffective - plannedHours);
  const friSummary = document.getElementById('fri-summary');
  if (friSummary) {
    const weekRemainingLive = Math.max(0, TARGET - liveWeekly);
    friSummary.innerHTML =
      `주간 누적 <span class="em">${fmtHours(liveWeekly)}</span>` +
      `<span class="sep">|</span>남은 시간 <span class="em">${fmtHours(weekRemainingLive)}</span>`;
  }
  const dailyNet = targetDay.leaveType === '반차' ? 4 : fridayRemaining;
  const checkinEl = document.getElementById('friday-checkin');
  // 실제 출근 시간이 확정되면 입력 필드에 반영
  if (checkinEl && targetDay.startTime && checkinEl.value !== padTime(targetDay.startTime)) {
    checkinEl.value = padTime(targetDay.startTime);
  }
  if (checkinEl?.value) updateFridayCheckout(checkinEl.value, netToGross(dailyNet));
}

// ─ 오류 렌더링 ────────────────────────────────────────────────────────────────

function renderError(msg) {
  const needsSetup = msg.includes('Client ID') || msg.includes('설정');
  document.getElementById('today-body').innerHTML = `
    <div class="error-box">
      ${escHtml(msg)}
      ${needsSetup
        ? `<br/><button class="btn-retry" id="err-settings">설정 열기</button>`
        : `<br/><button class="btn-retry" id="err-retry">다시 시도</button>`}
    </div>
  `;
  document.getElementById('day-list').innerHTML = '';
  document.getElementById('weekly-summary').textContent = '–';

  if (needsSetup) {
    document.getElementById('err-settings')?.addEventListener('click', () => chrome.runtime.openOptionsPage());
  } else {
    document.getElementById('err-retry')?.addEventListener('click', () => loadDashboard(false));
  }
}

// ── 빠른 휴가 추가 (주간 카드 헤더) ──────────────────────────────────────────

function onQuickLeave() {
  const date      = document.getElementById('ql-date').value;
  const leaveType = document.getElementById('ql-type').value;
  const btn       = document.getElementById('ql-submit');
  const msgEl     = document.getElementById('ql-msg');

  if (!date) { msgEl.textContent = '날짜를 선택해주세요'; msgEl.className = 'ql-msg err'; return; }

  btn.disabled = true;
  msgEl.textContent = '추가 중...';
  msgEl.className   = 'ql-msg';

  chrome.runtime.sendMessage({ action: 'addLeave', date, leaveType }, (response) => {
    btn.disabled = false;
    if (chrome.runtime.lastError || !response?.success) {
      msgEl.textContent = response?.error || '추가 실패';
      msgEl.className   = 'ql-msg err';
    } else {
      msgEl.textContent = `${date} ${leaveType} 완료`;
      msgEl.className   = 'ql-msg ok';
      setTimeout(() => {
        msgEl.textContent = '';
        document.getElementById('quick-leave-form').style.display = 'none';
      }, 2000);
      loadDashboard(true);
    }
  });
}

// ── 유틸리티 ─────────────────────────────────────────────────────────────────

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function formatTime(date) {
  return `${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`;
}

// "9:02" → "09:02" (캐시된 구 데이터도 표시 시점에 정규화)
function padTime(t) {
  if (!t) return t;
  const [h = '0', m = '00'] = String(t).split(':');
  return `${h.padStart(2, '0')}:${m.padStart(2, '0')}`;
}

function calcGrossHours(start, end) {
  const [sh, sm] = start.split(':').map(Number);
  const [eh, em] = end.split(':').map(Number);
  return ((eh * 60 + em) - (sh * 60 + sm)) / 60;
}

// 근로기준법 제54조 (역전 현상 방지)
// 4h/8h 순근무 달성 후 각 30분 휴게 구간 동안 net 고정
function applyBreak(gross) {
  if (gross <= 0)   return 0;
  if (gross >= 9)   return gross - 1;   // P5: 9h 이상 → 1h 공제
  if (gross >= 8.5) return 8;           // P4: 8h 순근무 달성 후 30분 휴게 구간 → 8h 고정
  if (gross > 4.5)  return gross - 0.5; // P3: 4.5h~8.5h → 30분 공제
  if (gross > 4)    return 4;           // P2: 4h 순근무 달성 후 30분 휴게 구간 → 4h 고정
  return gross;                          // P1: 4h 이하 → 공제 없음
}

function fmtHours(h) {
  if (h <= 0) return '0h';
  const hours = Math.floor(h);
  const mins  = Math.round((h - hours) * 60);
  if (mins === 0) return `${hours}h`;
  if (hours === 0) return `${mins}m`;
  return `${hours}h ${mins}m`;
}

function fmtHoursHtml(h) {
  if (h <= 0) return '<span class="dur-num">0</span>h';
  const hours = Math.floor(h);
  const mins  = Math.round((h - hours) * 60);
  const hPart = `<span class="dur-num">${hours}</span>h`;
  const mPart = mins > 0 ? `\u00A0<span class="dur-num">${mins}</span>m` : '';
  return hPart + mPart;
}

function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
