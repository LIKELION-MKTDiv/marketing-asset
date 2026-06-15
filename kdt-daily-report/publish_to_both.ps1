# KDT 데일리 리포트 — 생성 후 marketing-asset 두 레포(main)에 동시 발행
# 실행: ./publish_to_both.ps1
# 동작: ① 로컬 CSV로 리포트 생성  ② 두 레포 각각 clone→폴더 동기화→commit→push
#        (두 레포 main이 분기돼 있어 각 레포의 현재 main 위에 얹어 비파괴 푸시)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# 1) 리포트 생성 (reports/ + Obsidian 이중 출력)
Write-Host "[1] 리포트 생성..." -ForegroundColor Cyan
python generate_daily_report.py
if ($LASTEXITCODE -ne 0) { Write-Host "생성 실패 — CSV 경로/데이터 확인." -ForegroundColor Red; exit 1 }

# 2) 두 레포에 발행
$repos = @(
    "https://github.com/LIKELION-MKTDiv/marketing-asset.git",
    "https://github.com/whisky86/marketing-asset.git"
)
$src   = $PSScriptRoot
$today = Get-Date -Format "yyMMdd"
$env:GIT_TERMINAL_PROMPT = "0"

foreach ($url in $repos) {
    Write-Host "[2] 발행 → $url" -ForegroundColor Cyan
    $tmp = Join-Path $env:TEMP ("mktpub_" + [guid]::NewGuid().ToString("N").Substring(0,8))
    git clone --depth 1 $url $tmp
    if ($LASTEXITCODE -ne 0) { Write-Host "  clone 실패 — 권한/네트워크 확인. 건너뜀." -ForegroundColor Red; continue }

    # 로컬 kdt-daily-report 폴더를 레포 안으로 복사 (추가/덮어쓰기, 과거 리포트는 보존 — /E)
    robocopy $src (Join-Path $tmp "kdt-daily-report") /E /XD ".git" /NFL /NDL /NJH /NJS /NC /NS | Out-Null

    Push-Location $tmp
    git add kdt-daily-report
    $changes = git status --porcelain kdt-daily-report
    if ($changes) {
        git commit -m "report: KDT 모객현황 데일리 리포트 $today" | Out-Null
        git push origin HEAD:main
        if ($LASTEXITCODE -eq 0) { Write-Host "  푸시 완료 ($url)" -ForegroundColor Green }
        else { Write-Host "  푸시 실패 ($url) — 권한 확인." -ForegroundColor Red }
    } else {
        Write-Host "  변경 없음 — 커밋 생략." -ForegroundColor Yellow
    }
    Pop-Location
    Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
}
Write-Host "[완료] 두 레포 발행 처리 종료." -ForegroundColor Green
