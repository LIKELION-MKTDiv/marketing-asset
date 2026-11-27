# 브랜드 키트 작성법 (brand.json)

브랜드 담당자가 **브랜드당 한 번** 채웁니다. 디자인 가이드 문서를 옆에 두고 아래 순서로 값을 옮기세요. 확정 예시는 `brands/likelion/brand.json`과 `brands/likelion/DESIGN_GUIDE.md`입니다.

## 1. 캔버스와 안전 여백

```json
"canvas": {"width": 1080, "height": 1350},
"safe_area": {"top": 100, "right": 100, "bottom": 100, "left": 100}
```

- 인스타그램 피드 4:5 세로형이 기본입니다. 정사각형은 1080×1080으로 바꿉니다.
- `safe_area`는 본문 글자가 넘으면 안 되는 선입니다. 가이드에 여백 규정이 없으면 상하 100~150, 좌우 100~110px에서 시작하세요.
- 하단 티저 바(높이 104px)를 쓰는 브랜드는 `bottom`을 150 이상으로 둡니다.

## 2. 서체

```json
"fonts": {"family": "Pretendard", "css": "https://cdn.jsdelivr.net/npm/pretendard@1.3.9/dist/web/static/pretendard.min.css"}
```

- 웹폰트 CSS 주소를 넣으면 설치 없이 어느 PC에서나 같은 결과가 나옵니다.
- 브랜드 전용 서체가 웹폰트로 배포되어 있으면 그 CSS 주소를 넣고 `family`를 서체 이름으로 바꿉니다. 서체 파일만 있다면 웹폰트 CSS를 먼저 만들어 공유 위치에 올려 두는 것을 권장합니다(라이선스 확인 필수).

## 3. 색

```json
"colors": {"primary": "#FF6000", "secondary": "#1C1C1C", "accent": "#FFE066",
           "bg": "#1C1C1C", "text": "#FFFFFF", "ink": "#1C1C1C", "muted": "#B8B8B8",
           "panel": "#F9F9F9", "track": "#E6E1DA", "scrim": "rgba(28,28,28,.78)"}
```

| 키 | 쓰는 곳 |
|---|---|
| `primary` | 강조 글자(`.hl`), 차트 강조 막대, 스티커, 끝 장 티저 바 |
| `secondary` | 보조 막대, 기본 티저 바 |
| `accent` | 두 번째 강조(`.hl2`) |
| `bg` | 기본 배경 |
| `text` | 어두운 배경 위 기본 글자 |
| `ink`, `ink-2` | 밝은 패널 위 글자, 차트 글자 |
| `muted` | 라벨, 보조 정보 |
| `panel`, `track` | 흰 패널 배경, 차트 눈금·게이지 바탕 |
| `scrim` | 사진 위 글자 뒤 가독성 패널 |
| `bar`, `bar-end`, `bar-text` | (선택) 티저 바 색 |

키는 자유롭게 늘릴 수 있습니다. spec에서 `"color": "primary"`처럼 키 이름으로 부르면 브랜드가 바뀌어도 spec을 고칠 필요가 없습니다.

## 4. 글자 크기 체계 (type)

```json
"type": {
  "cover":  {"size": 90, "weight": 800, "line": 1.34},
  "h":      {"size": 65, "weight": 800, "line": 1.35},
  "sub":    {"size": 35, "weight": 700, "line": 1.45},
  "kicker": {"size": 40, "weight": 700, "line": 1.3, "color": "primary"}
}
```

- 키마다 `.t-키` 클래스가 생깁니다. spec 본문에서 `<div class='t-h'>제목</div>`처럼 씁니다.
- `size`는 캔바에 입력하는 폰트 크기 값(px)과 같습니다. 가이드가 "썸네일 90~100px"처럼 범위로 주면 아래값을 넣고, 한 줄에 들어가는 글자 수를 확인합니다.
- 한 줄 최대 글자 수(한글) ≈ 사용 폭 ÷ (크기 × 0.865). 예: 사용 폭 880px, 65px → 약 15자.
- `tracking`(자간), `color`는 선택입니다.

## 5. 로고

```json
"logo": {"files": {"white": "assets/logo_white.png", "black": "assets/logo_black.png"},
         "default": "white", "ink_width": 188, "bottom": 100}
```

- 투명 배경 PNG를 넣습니다. 엔진이 투명 여백을 잘라 **실제 로고 모양(잉크)** 너비를 `ink_width`에 맞춥니다. 원본 캔버스 크기로 맞추면 로고가 작아지는 문제를 막기 위해서입니다.
- 위치는 하단 중앙이 기본이고 `bottom`은 캔버스 아래에서 로고 아랫단까지 거리입니다.
- 슬라이드마다 spec에서 `"logo": "white" | "black" | "none"`으로 고릅니다. 배경 위 로고 조합 규정(예: 오렌지 배경엔 검정 로고)은 가이드를 따르세요.
- 로고가 없는 브랜드는 `"files": {}`, `"default": "none"`.

## 6. 공통 요소 (chrome)

```json
"chrome": {"handle": "@your_brand", "teaser_bar": true, "page_counter": true, "grain": true, "end_label": "@your_brand"}
```

| 항목 | 효과 |
|---|---|
| `handle` | 상단 중앙 계정명. 끄려면 `null` |
| `teaser_bar` | 하단 바. 슬라이드의 `next` 문구가 오른쪽에, 마지막 장은 `end_label` |
| `page_counter` | 바 왼쪽 `1/5` |
| `grain` | 아주 옅은 질감 |

## 7. 검수 기준 (audit)

```json
"audit": {"min_font_px": 35, "bg_percentile": 98, "large_px": 48,
          "contrast": {"default": 4.5, "large": 3.0, "#FF6000": 3.5}}
```

- `min_font_px`: 이보다 작은 본문 글자는 경고. 피드에서 축소 노출될 때 읽히는 하한으로 정합니다.
- `contrast.default`: 일반 글자 목표(웹 접근성 기준 4.5:1). `large`: `large_px` 이상 큰 글자 목표.
- 색별 예외: 중간 밝기 브랜드 색(예: 오렌지 `#FF6000`)은 검정 위에서도 5.83:1이 상한이라 4.5:1을 일괄 적용하면 쓸 수 없습니다. 가이드에서 정한 색별 목표를 `"#HEX": 값`으로 넣습니다.

## 8. DESIGN_GUIDE.md

`brand.json`의 숫자가 가이드 원문의 어디에서 왔는지 한 장으로 남깁니다. "확정 스펙(바꾸지 않음)"과 "파생 규칙(근거가 있으면 조정 가능)"을 나눠 적으면 다른 담당자가 이어받기 쉽습니다.
