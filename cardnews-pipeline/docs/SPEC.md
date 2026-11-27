# 콘텐츠 spec 작성법 (spec.json)

콘텐츠마다 새로 씁니다. `examples/`의 샘플을 폴더째 복사해 시작하세요.

```
examples/내콘텐츠/
├── spec.json
└── assets/        사진, 배경 플레이트 (spec에서 {A}로 부름)
```

## 기본 형태

```json
{
  "title": "콘텐츠 이름",
  "assets": {"cover": {"file": "IMG_0001.jpg", "mode": "photo"}},
  "slides": [
    {"id": "01_cover", "bg": {...}, "logo": "white", "next": "다음 장 티저", "html": "본문 HTML"}
  ],
  "charts": {"rank": {...}}
}
```

| 필드 | 설명 |
|---|---|
| `id` | 출력 파일 이름. 순서대로 `01_`, `02_` 접두사를 권장 |
| `bg` | 배경 (아래 표). 생략하면 브랜드 `bg` 색 |
| `logo` | `white` / `black` / `none`. 생략하면 브랜드 기본값 |
| `next` | 하단 티저 바 문구 (브랜드 `teaser_bar`가 켜져 있을 때). 마지막 장은 생략 |
| `html` | 본문. `.content` 안에 들어가며 안전 여백이 기본 패딩 |
| `handle` | `false`면 이 장만 상단 계정명 숨김 |

## 배경 (bg)

| 형식 | 예 | 용도 |
|---|---|---|
| 색 | `{"kind": "color", "value": "primary"}` | 브랜드 색 키 또는 #HEX |
| 그라데이션 | `{"kind": "gradient", "value": "linear-gradient(160deg,#2A2A2A,#1C1C1C)"}` | CSS 그대로 |
| 사진 풀블리드 | `{"kind": "photo", "src": "cover.jpg", "mode": "full", "position": "center 35%"}` | 아래쪽이 어두워져 하단 글자가 읽힘 |
| 사진 블러 | `{"kind": "photo", "src": "cover.jpg", "mode": "blur"}` | 패널·차트 장의 배경 |
| 사진 상단 | `{"kind": "photo", "src": "end.jpg", "mode": "top", "position": "center 40%", "height": 900}` | 얼굴은 위, 글자는 아래 바탕색 위 |
| 배경 플레이트 | `{"kind": "plate", "src": "plates/1cut.png"}` | 생성 AI로 만든 배경 이미지를 그대로 깖 |

`src`는 `assets/` 기준 상대 경로입니다.

## 본문 HTML에서 쓰는 것

| 쓰는 법 | 효과 |
|---|---|
| `<div class='t-h'>`, `t-cover`, `t-sub` ... | 브랜드 글자 크기 체계 (brand.json `type`의 키) |
| `<span class='hl'>` / `hl2` | 강조 색 primary / accent |
| `<div class='at' style='bottom:190px'>` | 안전 여백 좌우선에 맞춘 절대 배치. `top:`이나 `bottom:`만 주면 됨 |
| `<div class='scrim'>` | 사진·플레이트 위 글자 뒤 가독성 패널 (왼쪽 블리드, 오른쪽 페이드) |
| `<div class='panel'>` | 흰 카드. 차트·체크리스트를 넣음 |
| `<span class='pill'>`, `tag`, `num`, `sticker`, `btn` | 시리즈 이름, 사진 캡션, 번호 원, 넘김 스티커, CTA 버튼 |
| `{{chart:ID}}` | `charts`의 ID 차트를 그림 |
| `{A}/파일명`, `{B}/파일명` | 콘텐츠 자산 / 브랜드 자산 경로 |
| `data-free` 속성 | 이 요소는 여백 검사에서 제외 (의도한 풀블리드 장식만) |
| `data-audit="off"` 속성 | 이 요소는 모든 검수에서 제외 |

## 차트 (charts)

```json
"charts": {
  "rank":  {"type": "bars", "rows": [["A", 34], ["B", 17]], "max": 40, "unit": "%",
            "ticks": [0, 10, 20, 30, 40], "highlight": [0], "color": "primary", "color_rest": "secondary"},
  "gauge": {"type": "gauge", "unit": "%", "items": [{"value": 34, "label": "A · 1위", "color": "primary"}]}
}
```

- 차트는 밝은 `.panel` 안에 넣습니다. SVG 안 글자는 자동 명암비 검수에서 빠지기 때문입니다.
- 수치를 쓰면 같은 장에 출처를 적습니다.

## 사진 준비

원본 폴더에서 리사이즈·누끼를 만들어 `assets/`에 저장합니다. 원본은 수정하지 않습니다.

```bash
python -m cardnews.prep_assets --spec examples/내콘텐츠/spec.json --src "D:/원본사진"
```

`mode`가 `cutout`이면 배경을 제거합니다(`pip install rembg` 필요).
