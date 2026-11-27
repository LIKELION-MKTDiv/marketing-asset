# 새 브랜드 키트 템플릿

1. 이 폴더를 `brands/브랜드명/`으로 복사합니다.
2. `brand.json`의 `name`, `colors`, `type`, `safe_area`, `chrome.handle`을 내 브랜드 디자인 가이드 값으로 바꿉니다. 항목 설명은 [docs/BRAND_KIT.md](../../docs/BRAND_KIT.md).
3. 로고가 있으면 투명 배경 PNG를 `assets/`에 넣고 `logo.files`, `logo.default`를 채웁니다.
4. 가이드 원문에서 가져온 값과 근거를 이 README(또는 `DESIGN_GUIDE.md`)에 표로 남깁니다.
5. `examples/template-sample/`을 복사해 렌더해 보고, 검수 통과를 확인합니다.

```bash
python -m cardnews.render --brand brands/브랜드명 --spec examples/template-sample/spec.json --out out/test
```
