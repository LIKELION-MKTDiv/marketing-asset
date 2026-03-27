# Git 완전 기초 가이드

> 작성일: 2026-03-27 | Git을 처음 시작하는 분을 위한 설명서

---

## 1. Git이란?

**"파일의 역사를 기록하는 타임머신"**

소설을 쓴다고 상상해보세요.
- 오늘 3장까지 썼어요 → **저장(커밋)**
- 내일 결말을 바꿔보고 싶어요 → **브랜치(복사본)** 생성
- 팀원과 함께 쓰고 싶어요 → **GitHub(클라우드)** 에 올리기

---

## 2. 핵심 용어 정리

| 용어 | 비유 | 설명 |
|---|---|---|
| **Repository (레포)** | 책 한 권 + 수정 이력 전체 | Git으로 관리되는 폴더 전체 |
| **Commit (커밋)** | 중간저장 | 지금 상태를 "스냅샷"으로 기록하는 것 |
| **Branch (브랜치)** | 다른 결말 버전 | 원본을 건드리지 않고 새 흐름을 만드는 것 |
| **Merge (머지)** | 두 버전을 합치기 | 브랜치를 원본에 합치는 것 |
| **Remote (리모트)** | 클라우드 서버 | GitHub 같은 외부 저장소 |
| **Push (푸시)** | 클라우드에 올리기 | 내 컴퓨터 → GitHub |
| **Pull (풀)** | 클라우드에서 받기 | GitHub → 내 컴퓨터 |
| **Clone (클론)** | 통째로 복사 | GitHub에 있는 레포를 내 컴퓨터에 처음 받아오기 |

---

## 3. 현재 내 Workspace 상태 (2026-03-27 기준)

```
workspaces/
├── Amaranth_Check/          ✅ Git 있음 | GitHub: jungho-1488/Amaranth_Check  (개인)
├── claude-code-mastery/     ✅ Git 있음 | GitHub: jungho-1488/claude-code-mastery (개인)
├── marketing-asset/         ✅ Git 있음 | GitHub: hoya-pi/marketing-asset (마케팅 그룹 공유)
├── bigin_message_QA/        ❌ Git 없음
├── drop-extension/          ❌ Git 없음
├── ethnography_kyobo_20260324/ ❌ Git 없음
└── test/                    ❌ Git 없음
```

> ⚠️ `marketing-asset`의 GitHub 연결 정보에 Access Token이 노출되어 있음. 추후 교체 필요.

---

## 4. 기본 업무 순서 (혼자 작업할 때)

### Step 1 — 레포지토리 만들기 (처음 한 번만)

```
새 프로젝트를 시작한다
    │
    ▼
GitHub에서 새 레포지토리 생성
    │
    ▼
내 컴퓨터 폴더에서 git init  (Git 시작 선언)
    │
    ▼
git remote add origin [GitHub 주소]  (클라우드와 연결)
```

> **비유:** 새 공책을 사서(git init), 그 공책을 클라우드 드라이브와 연동(remote add)하는 것

---

### Step 2 — 매일 작업하는 흐름

```
파일 수정/추가
    │
    ▼
git add .              ← "이 변경사항들을 저장 목록에 올려줘"
    │
    ▼
git commit -m "메시지"  ← "지금 이 상태를 기록해줘 (메모 포함)"
    │
    ▼
git push               ← "기록한 내용을 GitHub에도 올려줘"
```

> **비유:**
> - `git add` = 택배 박스에 물건 담기
> - `git commit` = 박스 포장하고 송장 붙이기
> - `git push` = 택배 발송

**커밋 메시지 잘 쓰는 법:**
```
❌ "수정함"
❌ "업데이트"
✅ "로그인 버튼 색상 변경"
✅ "3월 캠페인 배너 이미지 추가"
```

---

### Step 3 — 브랜치는 언제 쓰나?

브랜치는 **"실험하거나, 기능을 따로 개발할 때"** 씁니다.

#### 브랜치가 필요한 상황

| 상황 | 이유 |
|---|---|
| 새 기능을 추가하는데 기존 것을 망치기 싫을 때 | 원본(`main`)은 안전하게 보존 |
| 팀원과 각자 다른 작업을 동시에 할 때 | 서로 충돌 없이 작업 가능 |
| 배포용과 개발용을 분리하고 싶을 때 | 안정 버전 유지 |

#### 혼자 작업한다면?

```
혼자 + 단순한 프로젝트   →  브랜치 없이 main에 직접 커밋해도 OK
혼자 + 실험적인 작업     →  브랜치 만들어서 해보고, 성공하면 main에 합치기
팀과 함께               →  반드시 브랜치 사용 권장
```

#### 브랜치 실전 흐름 (A 디렉토리 수정 예시)

```bash
# 1. 브랜치 만들면서 바로 이동 (-b 옵션)
git checkout -b feature/A수정

# 2. A 디렉토리 파일 수정
# ... 작업 ...

# 3. 변경사항 저장
git add .
git commit -m "A 디렉토리 레이아웃 수정"

# 4. 브랜치째로 GitHub에 올리기 (브랜치 이름 꼭 지정!)
git push origin feature/A수정

# 5. GitHub 웹사이트에서 Pull Request 생성
#    → 혼자면 본인이 바로 Merge
#    → 팀이면 팀원 검토 후 Merge

# 6. Merge 완료 후 로컬 정리
git checkout main              # main으로 돌아오기
git pull                       # main 최신 상태 받아오기
git branch -d feature/A수정   # 다 쓴 브랜치 삭제
```

#### 전체 흐름 그림

```
main ──────────────────────────────────────── Merge ──▶
         │                                     ▲
         └─ feature/A수정 ── commit ── push ── PR ──┘
```

> **포인트:**
> - `git push` (X) → `git push origin feature/A수정` (O)
> - Merge 후엔 브랜치 삭제해서 깔끔하게 관리
> - 다음 작업은 또 새 브랜치를 만들어서 시작

#### 브랜치 기본 명령어

```bash
git branch feature/새기능          # 브랜치 만들기
git checkout feature/새기능        # 그 브랜치로 이동
git checkout -b feature/새기능     # 만들기 + 이동 한번에
git checkout main                  # 원본으로 돌아오기
git merge feature/새기능           # 원본에 합치기 (로컬)
git branch -d feature/새기능       # 브랜치 삭제
```

---

## 5. 전체 흐름 한눈에 보기

```
[내 컴퓨터]                        [GitHub 서버]

  폴더 생성
     │
  git init
     │
  파일 작업
     │
  git add
     │
  git commit ──────── push ──────▶  레포지토리
                                        │
  파일 작업 ◀──────── pull ────────────┘
     │
  git add
     │
  git commit ──────── push ──────▶  (최신 상태 유지)
```

---

## 6. 자주 쓰는 명령어 모음

```bash
# 현재 상태 확인 (뭐가 바뀌었나?)
git status

# 변경 내용 상세히 보기
git diff

# 커밋 기록 보기
git log --oneline

# 브랜치 목록 보기
git branch

# 특정 시점으로 되돌리기 (주의!)
git checkout [커밋ID]
```

---

## 7. Push vs Pull Request — 헷갈리지 말기

이름이 비슷해서 자주 혼동되지만 **완전히 다른 개념**이에요.

| | Push | Pull Request (PR) |
|---|---|---|
| 종류 | 명령어 | 협업 프로세스 |
| 하는 일 | 내 컴퓨터 → GitHub 업로드 | "main에 합쳐주세요" 검토 요청 |
| 어디서 | 터미널 | GitHub 웹사이트 |
| 혼자 써도? | 매일 씀 | 팀 작업할 때 주로 씀 |

### 순서로 이해하기

```
작업
 │
 ▼
git commit       ← 내 컴퓨터에 저장
 │
 ▼
git push         ← GitHub에 올리기  (여기까지는 혼자)
 │
 ▼
Pull Request     ← "main에 합쳐주세요" 요청  (여기서 팀이 개입)
 │
 ▼
Merge            ← main에 최종 반영
```

> **비유:** Push는 회사 공유 폴더에 파일 올리는 것,
> PR은 "이 파일 최종본으로 써도 될까요?" 라고 팀장한테 결재 올리는 것.

**혼자 쓰는 개인 레포는 PR 없이 push만 해도 완전히 OK.**

---

## 8. marketing-asset 협업 시 주의사항

팀과 공유하는 레포는 **반드시 브랜치를 사용**하는 것을 권장해요.

```
main 브랜치        →  배포/공유 완료된 안정 버전
feature/내작업     →  내가 작업 중인 브랜치
```

작업 완료 후 `main`에 합칠 때는 **Pull Request(PR)** 를 통해
팀원의 확인을 받고 합치는 것이 일반적인 협업 방식이에요.

---

*이 문서는 `/Users/jungho/workspaces/Study/GIT_GUIDE.md` 에 저장되어 있어요.*
