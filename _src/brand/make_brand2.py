# -*- coding: utf-8 -*-
"""한국휴머나이저 새 로고(대표가 준 K 표지 + 한국휴머나이저 / HUMANIZER, 2026.11.21 22:00)로 사이트 그림 만들기
logo-source.png(흰 바탕) -> 흰색을 투명으로 바꿔
  docs/assets/img/logo-k.png      K 표지만(머리글 · 바닥글, 높이 138px)
  docs/assets/img/logo-full.png   로고 전체(공유 그림 · 상품 그림용, 투명)
  favicon.ico · favicon.svg · apple-touch-icon.png · logo-192/512.png  K 표지를 흰 바탕 정사각에
python3 _src/brand/make_brand2.py"""
import os, io, base64
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(ROOT, "docs", "assets", "img")
src = Image.open(os.path.join(HERE, "logo-source.png")).convert("RGB")


def white_to_alpha(im):
    """흰 바탕을 투명으로(색은 흰 바탕 위에서와 똑같이 보이게 되돌림)"""
    a = np.asarray(im).astype(np.float32) / 255.0
    alpha = np.max(1.0 - a, axis=-1)                      # 흰색에서 얼마나 떨어졌나
    alpha = np.clip((alpha - 0.02) / 0.98, 0, 1)           # 바탕의 아주 옅은 얼룩은 0으로
    safe = np.maximum(alpha, 1e-4)[..., None]
    rgb = 1.0 - (1.0 - a) / safe                           # 흰 바탕과 섞이기 전 색
    rgb = np.clip(rgb, 0, 1)
    out = np.concatenate([rgb, alpha[..., None]], -1)
    return Image.fromarray((out * 255).round().astype(np.uint8), "RGBA")


full = white_to_alpha(src.crop((130, 150, 2030, 604)))
full = full.crop(full.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
full.save(os.path.join(HERE, "logo-full.png"), optimize=True)
w = 1200; full.resize((w, round(full.height * w / full.width)), Image.LANCZOS).save(os.path.join(IMG, "logo-full.png"), optimize=True)

k = white_to_alpha(src.crop((135, 155, 790, 600)))
k = k.crop(k.getchannel("A").point(lambda v: 255 if v > 10 else 0).getbbox())
k.save(os.path.join(HERE, "logo-k.png"), optimize=True)
k.resize((round(k.width * 138 / k.height), 138), Image.LANCZOS).save(os.path.join(IMG, "logo-k.png"), optimize=True)


def square(size, pad, bg=(255, 255, 255, 255)):
    inner = round(size * (1 - 2 * pad))
    r = k.copy(); r.thumbnail((inner, inner), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), bg)
    out.alpha_composite(r, ((size - r.width) // 2, (size - r.height) // 2))
    return out


square(192, .1).convert("RGB").save(os.path.join(IMG, "logo-192.png"), optimize=True)
square(512, .1).convert("RGB").save(os.path.join(IMG, "logo-512.png"), optimize=True)
square(180, .1).convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
square(256, .04, (0, 0, 0, 0)).save(os.path.join(ROOT, "docs", "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
b = io.BytesIO(); square(96, .04, (0, 0, 0, 0)).save(b, "PNG", optimize=True)
open(os.path.join(IMG, "favicon.svg"), "w").write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96"><image width="96" height="96" href="data:image/png;base64,%s"/></svg>' % base64.b64encode(b.getvalue()).decode())
print("ok", full.size, k.size)
