# 🍴 GitHub Fork & 로컬 작업 가이드

> 팀 레포지토리를 Fork하여 내 계정으로 복사한 뒤, 로컬에서 작업하는 방법입니다.

---

## 1. Fork 하기 (GitHub 웹)

1. 원본 레포지토리 페이지에 접속
2. 우측 상단 **Fork** 버튼 클릭
3. Owner → **내 계정** 선택
4. `Create fork` 클릭

> ✅ 내 GitHub 계정에 동일한 레포가 복사됩니다.

---

## 2. 내 Fork를 로컬로 가져오기

### Cursor / VSCode 기준

1. 터미널 열기: `Ctrl + Shift + ``
2. 아래 명령어 입력:

```bash
# 내 Fork 주소로 클론
git clone https://github.com/내계정/레포명.git

# 폴더 이동
cd 레포명
```

---

## 3. 원본 레포 연결 (upstream 설정)

원본 레포의 최신 변경사항을 받기 위해 연결해둡니다.

```bash
# 원본 레포를 upstream으로 등록
git remote add upstream https://github.com/원본계정/레포명.git

# 연결 확인
git remote -v
```

출력 예시:
```
origin    https://github.com/내계정/레포명.git (fetch)
origin    https://github.com/내계정/레포명.git (push)
upstream  https://github.com/원본계정/레포명.git (fetch)
upstream  https://github.com/원본계정/레포명.git (push)
```

---

## 4. 작업 브랜치 만들기

```bash
# main 브랜치 최신화
git checkout main
git pull upstream main

# 작업 브랜치 생성 & 이동
git checkout -b feature/작업내용
```

---

## 5. 작업 → 커밋 → 푸시

```bash
# 변경사항 확인
git status

# 전체 스테이징
git add .

# 커밋
git commit -m "작업 내용 요약"

# 내 Fork로 푸시
git push origin feature/작업내용
```

---

## 6. Pull Request 보내기

1. GitHub에서 **내 Fork** 페이지 접속
2. 상단에 나타나는 `Compare & pull request` 버튼 클릭
3. 변경 내용 작성 후 `Create pull request`

---

## 7. 원본 레포 최신화 (수시로)

다른 팀원의 변경사항을 내 Fork에 반영할 때:

```bash
git checkout main
git pull upstream main
git push origin main
```

---

## 📌 한눈에 보는 전체 흐름

```
원본 레포 (upstream)
    │
    ├── Fork ──→ 내 레포 (origin)
    │                │
    │                ├── git clone ──→ 로컬
    │                │                  │
    │                │          작업 → commit → push
    │                │                  │
    │                ◀── push ─────────┘
    │
    ◀── Pull Request ──────────────────┘
```

---

## ⚠️ 주의사항

| 항목 | 설명 |
|---|---|
| **직접 push 금지** | 원본 레포에 직접 push하지 않기. 반드시 PR로 요청 |
| **브랜치 이름** | `feature/기능명`, `fix/버그명` 형식 권장 |
| **충돌 발생 시** | `git pull upstream main` 후 로컬에서 충돌 해결 → 다시 push |
| **Fork 최신화** | 작업 시작 전에 항상 `git pull upstream main` 실행 |
