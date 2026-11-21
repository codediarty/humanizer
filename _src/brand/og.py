# -*- coding: utf-8 -*-
"""공유 그림(og.png 1200x630): 로봇 로고 + 새 첫 화면 문구(2026.11.21 밤). python3 _src/brand/og.py"""
import os, asyncio
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONT = "file://" + os.path.join(ROOT, "_src", "shop", "pretendard.css")
ROBOT = "file://" + os.path.join(HERE, "robot.png")
HTML = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="%s"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{width:1200px;height:630px;overflow:hidden;font-family:'Pretendard Variable',Pretendard,sans-serif;-webkit-font-smoothing:antialiased;letter-spacing:-.02em;color:#fff;
 background:radial-gradient(700px 420px at 92%% 30%%,rgba(30,136,255,.32),transparent 65%%),radial-gradient(620px 380px at 0%% 105%%,rgba(14,159,110,.22),transparent 60%%),#0a1224;position:relative}
.lk{position:absolute;left:76px;top:70px;display:flex;align-items:center;gap:16px}
.lk img{height:66px}
.lk b{display:block;font-size:34px;font-weight:800;letter-spacing:-.035em;line-height:1}
.lk i{display:flex;justify-content:space-between;margin-top:7px;font-style:normal;font-size:19px;font-weight:800;color:#5fb0ff;line-height:1}
h1{position:absolute;left:76px;top:200px;font-size:66px;line-height:1.16;font-weight:800;letter-spacing:-.045em}
p{position:absolute;left:78px;top:388px;font-size:25px;line-height:1.55;color:#a9b6cc;font-weight:500}
.chips{position:absolute;left:78px;bottom:70px;display:flex;gap:12px}
.chips span{height:46px;padding:0 20px;border-radius:23px;display:flex;align-items:center;font-size:21px;font-weight:700;border:1.5px solid rgba(255,255,255,.22);color:#e2e8f0}
.chips span:first-child{background:#0e9f6e;border-color:#0e9f6e;color:#fff}
.rb{position:absolute;right:40px;top:70px;height:440px}
.card{position:absolute;right:70px;bottom:52px;width:390px;background:#fff;border-radius:22px;padding:18px 22px;color:#0b1730;box-shadow:0 30px 60px -20px rgba(0,0,0,.6);display:flex;align-items:center;gap:16px}
.card small{display:block;font-size:16px;font-weight:700;color:#64748b}
.card b{font-size:40px;font-weight:850;letter-spacing:-.04em}
.card .a{color:#fc0068}.card .z{color:#0e9f6e}
.card em{margin-left:auto;font-style:normal;background:#0e9f6e;color:#fff;font-size:17px;font-weight:800;padding:8px 12px;border-radius:10px}
</style></head><body>
<div class="lk"><img src="%s" alt=""><div><b>한국휴머나이저</b><i><span>H</span><span>U</span><span>M</span><span>A</span><span>N</span><span>I</span><span>Z</span><span>E</span><span>R</span></i></div></div>
<h1>AI 작성률은 낮추고,<br>원문의 의미는 그대로.</h1>
<p>킬러에서 검출되는 AI 패턴을 분석해 문장을 바꾸는<br>한국어 전용 휴머나이징 서비스</p>
<div class="chips"><span>무료 AI 작성률 검사</span><span>한글 · 워드 · PDF</span></div>
<img class="rb" src="%s" alt="">
<div class="card"><div><small>AI 작성률(실측 예시)</small><b><span class="a">92%%</span> → <span class="z">7%%</span></b></div><em>AI 미검출</em></div>
</body></html>"""


async def main():
    path = os.path.join(HERE, "_og.html")
    open(path, "w", encoding="utf-8").write(HTML % (FONT, ROBOT, ROBOT))
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        await pg.goto("file://" + path)
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=os.path.join(ROOT, "docs", "assets", "img", "og.png"))
        await b.close()
    print("ok")

asyncio.run(main())
