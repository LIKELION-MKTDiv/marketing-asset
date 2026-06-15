# KDT 모객현황 데일리 리포트 — 원클릭 생성 + GitHub 푸시
# 실행: ./run_and_push.ps1
$ErrorActionPreference = "Stop"

# 1) 리포트 생성 (레포 reports/ + Obsidian 폴더 이중 출력)
Set-Location $PSScriptRoot
Write-Host "[1/3] 리포트 생성 중..." -ForegroundColor Cyan
python generate_daily_report.py
if ($LASTEXITCODE -ne 0) { Write-Host "생성 실패 — CSV 경로/데이터를 확인하세요." -ForegroundColor Red; exit 1 }

# 2) 변경분 스테이징
$repoRoot = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $repoRoot
git add kdt-daily-report

$changes = git status --porcelain kdt-daily-report
if (-not $changes) {
    Write-Host "[2/3] 변경 사항 없음 — 커밋/푸시 생략." -ForegroundColor Yellow
    exit 0
}

# 3) 커밋 + 푸시
$today = Get-Date -Format "yyMMdd"
Write-Host "[2/3] 커밋: report: KDT 모객현황 데일리 리포트 $today" -ForegroundColor Cyan
git commit -m "report: KDT 모객현황 데일리 리포트 $today"
Write-Host "[3/3] GitHub 푸시 중..." -ForegroundColor Cyan
git push
if ($LASTEXITCODE -eq 0) {
    $origin = (git remote get-url origin)
    Write-Host "완료 — $origin (kdt-daily-report/reports)" -ForegroundColor Green
} else {
    Write-Host "푸시 실패 — git 인증을 확인하세요." -ForegroundColor Red; exit 1
}
