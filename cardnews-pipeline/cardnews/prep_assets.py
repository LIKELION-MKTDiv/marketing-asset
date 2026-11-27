# -*- coding: utf-8 -*-
"""카드뉴스 이미지 준비: 원본 폴더(읽기 전용)에서 리사이즈·누끼를 만들어 spec 옆 assets/에 저장한다.

사용:
  python -m cardnews.prep_assets --spec examples/my-post/spec.json --src "D:/원본사진폴더"

spec.json의 "assets"에 쓸 사진을 적는다.
  "assets": {"cover": {"file": "IMG_0001.jpg", "mode": "photo"},
             "dog":   {"file": "IMG_0002.jpg", "mode": "cutout"}}
  photo  -> assets/cover.jpg (긴 변 1600px)
  cutout -> assets/dog.png  (배경 제거, rembg 필요: pip install rembg)
원본 파일은 수정하지 않는다. 이미 만든 파일은 건너뛴다(다시 만들려면 지우고 실행).
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps


def load(path: Path, max_side=1600):
    im = Image.open(path)
    im.draft('RGB', (max_side, max_side))
    im = ImageOps.exif_transpose(im).convert('RGB')
    im.thumbnail((max_side, max_side))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--src', required=True, help='원본 사진 폴더')
    a = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    spec_path = Path(a.spec)
    spec = json.loads(spec_path.read_text(encoding='utf-8'))
    out = spec_path.parent / 'assets'
    out.mkdir(parents=True, exist_ok=True)
    session = None
    for key, item in spec.get('assets', {}).items():
        mode = item.get('mode', 'photo')
        dst = out / (key + ('.png' if mode == 'cutout' else '.jpg'))
        if dst.exists():
            continue
        im = load(Path(a.src) / item['file'], item.get('max_side', 1600))
        if mode == 'cutout':
            try:
                from rembg import new_session, remove
            except ImportError:
                sys.exit('cutout 모드는 rembg가 필요합니다: pip install rembg')
            session = session or new_session('isnet-general-use')
            cut = remove(im, session=session, post_process_mask=True)
            cut.crop(cut.getbbox()).save(dst)
        else:
            im.save(dst, quality=88)
        print('ok', key, dst.name)


if __name__ == '__main__':
    main()
