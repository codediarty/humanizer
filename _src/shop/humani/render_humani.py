# -*- coding: utf-8 -*-
"""Humani 아임웹 상품 그림(158~161) 다시 그리기 (2026.11.21 밤 대표: 오른쪽 '휴머나이징 전 → 후' 상자 빼고, 그림 속 '카피킬러' 문구 빼기)
기존 Humani 그림(Humani 세션 작업)의 구성 · 색은 그대로 따르고 두 가지만 뺌. python3 render_humani.py -> out/humani-<id>-1x1.jpg"""
import os, asyncio
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
FONT = "file://" + os.path.join(os.path.dirname(HERE), "pretendard.css")
P = [
    {"id": "lt", "name": "라이트", "tok": "100", "per": "토큰당 99원", "price": "9,900원", "list": "19,800원", "badge": ("정가의 50%", "o"), "note": "짧은 과제 · 자기소개서 한두 문항"},
    {"id": "pl", "name": "플러스", "tok": "350", "per": "토큰당 약 57원", "price": "19,900원", "list": "39,800원", "badge": ("정가의 50%", "o"), "note": "레포트 여러 편 · 자소서 한 세트"},
    {"id": "pr", "name": "프로", "tok": "1,000", "per": "토큰당 약 40원", "price": "39,900원", "list": "79,800원", "badge": ("BEST 추천", "y"), "save": "플러스보다 토큰당 약 30% 절약"},
    {"id": "mx", "name": "맥스", "tok": "2,000", "per": "토큰당 약 34원", "price": "69,900원", "list": "139,800원", "badge": ("최고 혜택", "w"), "save": "플러스보다 토큰당 약 40% 절약"},
]
CHECK = '<svg viewBox="0 0 24 24" width="22" height="22"><path d="M20 6 9 17l-5-5" fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>'
PEN = '<svg viewBox="0 0 24 24" width="30" height="30"><path d="M12 20h9M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4Z" fill="none" stroke="#34d399" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
LOGO = ('<svg viewBox="0 0 40 40" width="76" height="76"><rect width="40" height="40" rx="10" fill="#0f1b3d" stroke="rgba(255,255,255,.18)"/>'
        '<path d="M12 11v18M28 11v18M12 20h16" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>'
        '<circle cx="31.5" cy="31.5" r="5.5" fill="#10b981" stroke="#0f1b3d" stroke-width="2"/><path d="m29.2 31.6 1.6 1.6 3-3.2" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def html(p):
    bt, bk = p["badge"]
    left = ('<div class="save">%s</div>' % p["save"]) if p.get("save") else ('<div class="note">%s</div>' % p["note"])
    small = len(p["tok"]) > 3
    chips = "".join('<span>%s%s</span>' % (CHECK, t) for t in ["월 구독 없음", "쓴 만큼만 차감", "5년 사용", "결제 30초"])
    return """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="%s"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:1200px;height:1200px;overflow:hidden;position:relative;font-family:'Pretendard Variable',Pretendard,sans-serif;-webkit-font-smoothing:antialiased;letter-spacing:-.02em;background:#eef2f7}
.top{position:absolute;left:0;top:0;width:1200px;height:800px;background:radial-gradient(640px 420px at 100%% 0%%,rgba(124,58,237,.55),transparent 70%%),radial-gradient(700px 520px at 0%% 75%%,rgba(16,185,129,.28),transparent 65%%),linear-gradient(180deg,#0b1430 0%%,#0d1a3a 100%%)}
.top:after{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.07) 1.2px,transparent 1.2px);background-size:28px 28px}
.brand{position:absolute;left:85px;top:72px;display:flex;align-items:center;gap:20px;z-index:2;color:#fff}
.brand b{display:block;font-size:50px;font-weight:800;letter-spacing:-.03em;line-height:1}
.brand small{display:block;font-size:15px;font-weight:700;letter-spacing:.32em;color:#94a3b8;margin-top:9px}
.badge{position:absolute;right:85px;top:86px;height:58px;padding:0 28px;border-radius:29px;display:flex;align-items:center;font-size:27px;font-weight:800;z-index:2}
.badge.y{background:#fbbf24;color:#1a1a1a}.badge.w{background:#fff;color:#0b1730}.badge.o{background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.35);color:#e2e8f0}
.kind{position:absolute;left:87px;top:212px;display:flex;align-items:center;gap:12px;color:#e2e8f0;font-size:31px;font-weight:700;z-index:2}
.pills{position:absolute;left:85px;top:283px;display:flex;gap:14px;z-index:2}
.pill{height:56px;padding:0 26px;border-radius:28px;display:flex;align-items:center;font-size:28px;font-weight:800}
.pill.n{background:#10b981;color:#fff}.pill.o{border:2px solid rgba(255,255,255,.32);color:#fff;font-weight:700}
.big{position:absolute;left:78px;top:352px;display:flex;align-items:flex-end;color:#fff;z-index:2}
.big b{font-size:%dpx;font-weight:850;letter-spacing:-.06em;line-height:1}
.big span{font-size:64px;font-weight:800;margin:0 0 26px 18px}
.save{position:absolute;left:85px;top:640px;height:54px;padding:0 22px;border-radius:12px;border:2px solid rgba(251,191,36,.75);background:rgba(251,191,36,.08);color:#fcd34d;font-size:26px;font-weight:800;display:flex;align-items:center;z-index:2}
.note{position:absolute;left:87px;top:650px;color:rgba(255,255,255,.8);font-size:27px;font-weight:600;z-index:2}
.card{position:absolute;left:58px;top:724px;width:1084px;height:418px;background:#fff;border-radius:38px;box-shadow:0 30px 60px -28px rgba(11,23,48,.45);padding:52px 54px}
.card h2{font-size:54px;font-weight:850;letter-spacing:-.04em;color:#0b1730;line-height:1.1}
.card .s{font-size:30px;font-weight:600;color:#475569;margin-top:16px}
.chips{display:flex;gap:12px;margin-top:40px}
.chips span{height:50px;padding:0 20px;border-radius:25px;background:#f1f5f9;display:flex;align-items:center;gap:8px;font-size:23px;font-weight:700;color:#334155}
.ft{position:absolute;left:54px;right:54px;bottom:44px;display:flex;align-items:flex-end;justify-content:space-between}
.dom{font-size:31px;font-weight:800;color:#0e9f6e}.dom small{font-size:21px;font-weight:600;color:#94a3b8;margin-left:12px}
.pr{text-align:right}.pr del{display:block;font-size:25px;font-weight:600;color:#94a3b8;text-decoration-thickness:2px;margin-bottom:4px}
.pr .row{display:flex;align-items:baseline;gap:16px;justify-content:flex-end}.pr .off{font-size:48px;font-weight:850;color:#f43f5e}.pr b{font-size:76px;font-weight:850;letter-spacing:-.04em;color:#0b1730;line-height:1}
</style></head><body>
<div class="top"></div>
<div class="brand">%s<div><b>Humani</b><small>AI HUMANIZER</small></div></div>
<div class="badge %s">%s</div>
<div class="kind">%s AI 휴머나이징 토큰</div>
<div class="pills"><div class="pill n">%s</div><div class="pill o">%s</div></div>
<div class="big"><b>%s</b><span>토큰</span></div>
%s
<div class="card"><h2>AI 작성률 낮추기</h2><div class="s">AI 휴머나이징 · AI 글 인간화 토큰</div><div class="chips">%s</div>
<div class="ft"><div class="dom">humanai.io.kr<small>Humani(휴머나이)</small></div><div class="pr"><del>정가 %s</del><div class="row"><span class="off">50%%</span><b>%s</b></div></div></div></div>
</body></html>""" % (FONT, 236 if small else 262, LOGO, bk, bt, PEN, p["name"], p["per"], p["tok"], left, chips, p["list"], p["price"])


async def main():
    async with async_playwright() as pw:
        br = await pw.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await br.new_page(viewport={"width": 1200, "height": 1200})
        for p in P:
            f = os.path.join(HERE, "_h_%s.html" % p["id"])
            open(f, "w", encoding="utf-8").write(html(p))
            await pg.goto("file://" + f); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=os.path.join(OUT, "humani-%s-1x1.jpg" % p["id"]), type="jpeg", quality=92)
            os.remove(f)
        await br.close()
    print("ok", sorted(os.listdir(OUT)))

asyncio.run(main())
