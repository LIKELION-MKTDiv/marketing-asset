# TIL 블로그 크롤러

## 개요
구글 시트에서 블로그 URL을 읽어 제목과 해시태그를 자동으로 추출하는 크롤러

## 지원 플랫폼
- 벨로그 (velog.io)
- 티스토리 (tistory.com)
- 네이버 블로그 (blog.naver.com)

## 판별 기준

### K열 - 제목
- `멋쟁이사자처럼부트캠프` + 교육과정명 둘 다 있으면 → **O**
- `멋쟁이사자처럼부트캠프` 만 있으면 → **△**
- 둘 다 없으면 → **X**
- 노션 페이지 → **X**

### L열 - 해시태그
- `#멋쟁이사자처럼후기` + 스킬태그 둘 다 있으면 → **O**
- 둘 중 하나라도 있으면 → **△**
- 아무 해시태그도 없으면 → **X**
- 노션 페이지 → **X**

## 구조
```
구글 시트 URL 열 읽기
    ↓
플랫폼 감지 (벨로그 / 티스토리 / 네이버)
    ↓
Playwright로 크롤링
    ↓
제목 / 해시태그 추출
    ↓
구글 시트에 결과 기록
```

## 시트 구조 (예정)
| 열 | 내용 |
|----|------|
| A  | 이름 |
| B  | 블로그 URL |
| C  | 제목 (크롤링 결과) |
| D  | 해시태그 (크롤링 결과) |

## 교육과정별 스킬 매핑 테이블
| 교육과정 | 인정 해시태그 |
|---------|-------------|
| 그로스마케팅 | #마케팅 #그로스마케팅 #Growth #GA4 #SEO #콘텐츠마케팅 |
| 백엔드 | #Java #Spring #Python #Django #FastAPI #Node.js #SpringBoot #MySQL #PostgreSQL |
| 자바 | #Java #SpringBoot #Spring #JPA #MySQL |
| 프론트엔드 | #HTML #CSS #JavaScript #TypeScript #React #Vue #Next.js |
| 안드로이드 | #Android #Kotlin #Java #AndroidStudio |
| 클라우드 AWS | #AWS #Cloud #Docker #Kubernetes #DevOps #Linux #Terraform |
| 유니티 게임 | #Unity #C# #GameDev #게임개발 |
| UX/UI 디자인 | #Figma #UX #UI #디자인 #Prototyping |
| AI | #Python #AI #MachineLearning #DeepLearning #LLM #PyTorch #TensorFlow |
| PM | #PM #기획 #ProductManagement #애자일 #Scrum |

## 개인정보 보호
- 시트에 `Email`, `Phone number` 열이 있을 경우 해당 값은 마스킹 처리
- 크롤링 결과에 개인정보가 포함되지 않도록 주의
- 마스킹 대상 헤더: `Email`, `Phone number`

## 사용 방법
```bash
python crawl.py
```

## 필요 라이브러리
- `playwright`
- `gspread`
- `python-dotenv`
