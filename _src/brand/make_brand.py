# -*- coding: utf-8 -*-
"""한국휴머나이저 로봇 로고(대표가 준 캐릭터, 2026.11.21 밤)로 사이트 아이콘 · 로고 그림 만들기
python3 _src/brand/make_brand.py  ->  docs/assets/img/logo-robot.png · logo-192/512.png · apple-touch-icon.png · favicon.svg · docs/favicon.ico"""
import os, io, base64
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = os.path.join(ROOT, "docs", "assets", "img")
SRC = Image.open(os.path.join(HERE, "robot_green.png")).convert("RGBA")   # 2026.11.21 21:49 초록으로 통일(파란 원본 robot.png)   # 투명 배경, 여백 잘라 둔 원본(969x1039)


def fit(h):
    return SRC.resize((round(SRC.width * h / SRC.height), h), Image.LANCZOS)


def square(size, pad, bg=None):
    """정사각 칸 가운데에 로봇(pad = 바깥 여백 비율)"""
    inner = round(size * (1 - 2 * pad))
    r = SRC.copy(); r.thumbnail((inner, inner), Image.LANCZOS)
    out = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
    out.alpha_composite(r, ((size - r.width) // 2, (size - r.height) // 2))
    return out


# 머리글 · 바닥글 로고(화면 48px 높이의 3배)
fit(144).save(os.path.join(IMG, "logo-robot.png"), optimize=True)
# 앱 아이콘 · 구조화 데이터 로고: 흰 바탕 정사각
square(192, .08, (255, 255, 255, 255)).convert("RGB").save(os.path.join(IMG, "logo-192.png"), optimize=True)
square(512, .08, (255, 255, 255, 255)).convert("RGB").save(os.path.join(IMG, "logo-512.png"), optimize=True)
square(180, .09, (255, 255, 255, 255)).convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
# 파비콘: ico(16 · 32 · 48, 투명) + svg(64px 그림을 담은 svg)
square(256, .0).save(os.path.join(ROOT, "docs", "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)])
b = io.BytesIO(); square(96, .0).save(b, "PNG", optimize=True)
svg = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 96 96">'
       '<image width="96" height="96" href="data:image/png;base64,%s"/></svg>') % base64.b64encode(b.getvalue()).decode()
open(os.path.join(IMG, "favicon.svg"), "w").write(svg)
print("ok", [f for f in os.listdir(IMG)])
