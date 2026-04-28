# TIL 블로그 크롤러

구글 시트에 입력된 블로그 URL을 자동으로 크롤링하여 제목과 해시태그를 판별하고, K·L·M열에 결과를 기록하는 도구입니다.

---

## 지원 플랫폼

| 플랫폼 | 도메인 |
|--------|--------|
| 벨로그 | velog.io |
| 티스토리 | tistory.com |
| 네이버 블로그 | blog.naver.com |
| 기타 블로그 | 공통 선택자로 시도 |

> 노션(notion.so), GitHub(github.io, github.com), Oopy(oopy.io)는 블로그 포스팅으로 인정하지 않으며 자동으로 **X** 처리됩니다.

---

## 시트 구조

| 열 | 내용 |
|----|------|
| A  | 블로그 URL |
| B  | 교육과정명 |
| C  | 기수 |
| K  | 제목 판별 결과 (O / △ / X) |
| L  | 해시태그 판별 결과 (O / △ / X) |
| M  | 비고 (판별 사유) |

데이터 시작 행: **55행** (`START_ROW` 상수로 변경 가능)

---

## 판별 기준

### K열 — 제목

| 조건 | 결과 |
|------|------|
| `멋쟁이사자처럼부트캠프` + 교육과정명 둘 다 포함 | **O** |
| `멋쟁이사자처럼부트캠프`만 포함 (교육과정명 없음) | **△** |
| 브랜드명 없음 | **X** |
| 노션 등 인정 불가 플랫폼 | **X** |

### L열 — 해시태그

| 조건 | 결과 |
|------|------|
| `#멋쟁이사자처럼후기` + 스킬 해시태그 둘 다 포함 | **O** |
| 둘 중 하나만 있음 | **△** |
| 아무 해시태그도 없음 | **X** |
| 노션 등 인정 불가 플랫폼 | **X** |

---

## 교육과정별 스킬 매핑

현재 `COURSE_SKILL_MAP`에 정의된 인정 해시태그 목록입니다.

| 교육과정 | 인정 해시태그 |
|---------|-------------|
| 그로스마케팅 | #마케팅 #그로스마케팅 #growth #ga4 #seo #콘텐츠마케팅 |
| 백엔드 | #java #spring #python #django #fastapi #node.js #springboot #mysql #postgresql |
| 자바 | #java #springboot #spring #jpa #mysql |
| 프론트엔드 | #html #css #javascript #typescript #react #vue #next.js |
| 안드로이드 | #android #kotlin #java #androidstudio |
| 클라우드 / AWS | #aws #cloud #docker #kubernetes #devops #linux #terraform |
| 유니티 / 게임 | #unity #c# #gamedev #게임개발 |
| UX/UI / 디자인 | #figma #ux #ui #디자인 #prototyping |
| AI | #python #ai #machinelearning #deeplearning #llm #pytorch #tensorflow |
| PM | #pm #기획 #productmanagement #애자일 #scrum |

> 비교 시 대소문자 및 공백·특수문자를 제거한 후 매칭합니다 (`normalize()` 함수 참고).

---

## 개선 제안

### `#` 태그 자체를 인정하는 로직 보강

현재 L열 판별은 **매핑 테이블에 등록된 스킬 태그**가 있어야 O/△를 줍니다.  
그러나 수강생이 `#멋쟁이사자처럼후기` 외에 `#부트캠프`, `#개발공부` 등 매핑에 없는 해시태그를 달았을 때도 **`#` 기호로 시작하는 태그가 존재한다는 사실 자체**는 성실하게 포스팅한 근거로 볼 수 있습니다.

**현재 동작**
```
#멋쟁이사자처럼후기 #부트캠프 #개발일지
→ L열: △  (스킬 매핑 태그 없음)
```

**보강 방향 (예시)**

```python
def check_hashtags(tags_text, course_name=''):
    tags_lower = normalize(tags_text)
    has_required = normalize(REQUIRED_HASHTAG) in tags_lower

    # 매핑 스킬 태그 여부
    skill_tags = COURSE_SKILL_MAP.get(normalize(course_name), [])
    has_skill = any(normalize(t) in tags_lower for t in skill_tags)

    # #으로 시작하는 태그가 필수태그 외에도 존재하는지 확인
    other_hash_tags = [t for t in tags_text.split() if t.startswith('#') and t != REQUIRED_HASHTAG]
    has_any_hash = bool(other_hash_tags)

    if has_required and has_skill:
        return 'O', ''
    elif has_required and has_any_hash:
        # 스킬 매핑엔 없지만 #태그는 사용 중 → O 또는 별도 기호로 구분 가능
        return 'O', f'매핑 외 태그 사용: {" ".join(other_hash_tags)}'
    elif has_required:
        return '△', f'{REQUIRED_HASHTAG}만 있고 다른 태그 없음'
    else:
        return 'X', f'{REQUIRED_HASHTAG} 미포함 (태그: "{tags_text}")'
```

> M열 비고에 `매핑 외 태그 사용: #부트캠프 #개발일지` 형태로 남기면, 나중에 자주 등장하는 태그를 매핑 테이블에 추가하는 기준 자료로도 활용할 수 있습니다.

---

## 설치 및 실행

### 1. 패키지 설치

```bash
pip install google-auth google-auth-oauthlib google-api-python-client playwright
playwright install chromium
```

| 패키지 | 용도 |
|--------|------|
| `google-auth` | 구글 OAuth 토큰 관리 |
| `google-auth-oauthlib` | 최초 인증 흐름 처리 |
| `google-api-python-client` | Sheets API 호출 (`googleapiclient`) |
| `playwright` | 블로그 크롤링 (headless 브라우저) |

> `gspread`는 **사용하지 않습니다.** Sheets API를 직접 호출합니다.

---

### 2. 구글 인증 설정 (최초 1회)

**Google Cloud Console에서 준비할 것**

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 생성 또는 선택
3. **APIs & Services → 라이브러리** → `Google Sheets API` 활성화
4. **APIs & Services → 사용자 인증 정보** → `OAuth 2.0 클라이언트 ID` 생성
   - 애플리케이션 유형: **데스크톱 앱**
5. JSON 파일 다운로드 → 프로젝트 **상위 폴더**에 `google_credentials.json`으로 저장

```
프로젝트 구조 예시
Claude/
├── google_credentials.json   ← 여기에 위치
├── token.json                ← 최초 실행 후 자동 생성
└── project/
    └── til/
        └── til_crawler.py
```

> `token.json`은 최초 실행 시 브라우저 인증 창이 뜨면서 자동 생성됩니다. 이후엔 자동으로 재사용·갱신됩니다.

---

### 3. 상수 설정

`til_crawler.py` 상단의 상수를 시트 상황에 맞게 수정합니다.

```python
SPREADSHEET_ID = '시트 URL에서 복사한 ID'
SHEET_NAME     = '탭 이름'
START_ROW      = 55   # 헤더 제외 데이터 시작 행
```

---

### 4. 실행

```bash
python til_crawler.py
```

---

## 개인정보 보호

- 시트에 이름·연락처·이메일 열이 포함된 경우 해당 값은 컨텍스트에 올리지 않음
- 크롤링 결과에 개인정보가 포함되지 않도록 주의
