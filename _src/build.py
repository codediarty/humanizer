# -*- coding: utf-8 -*-
"""한국휴머나이저(humanizer.co.kr) 정적 사이트 만들기

    python3 _src/build.py

docs/ 에 페이지 · sitemap.xml · robots.txt · llms.txt · rss.xml 을 씁니다(GitHub Pages 가 docs/ 를 그대로 서빙).
검사 · 휴머나이징 엔진은 AIMarker 서버와 같은 엔진(Apps Script 'AIMarker 서버' 프로젝트, 한국휴머나이저 배포)을 씁니다.
"""
import datetime
import difflib
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs")
sys.path.insert(0, HERE)
from icons import ICONS  # noqa: E402
import pages as P  # noqa: E402

# ---------------- 설정 ----------------
SITE = "https://humanizer.co.kr"
BRAND = "한국휴머나이저"
BRAND_EN = "Korea Humanizer"
VER = "20261121a"
TODAY = "2026-11-21"
API = "https://script.google.com/macros/s/AKfycbwo5wo2gZGCAj3XGLaKfzxZOqHVIkyh9slHiguF_lBO_OKKUpn_GLbW0oOpujatwWtmNw/exec"
SHOP = "https://skkc.co.kr/shop_view?idx=%s&kaiec_buy=1"
# 성균관컨설팅(아임웹) 한국휴머나이저 전용 상품 번호. 서버는 스크립트 속성 HZ_IDX 로 같은 번호를 hz1~hz4 로 봄
SHOP_IDX = {"lt": "157", "pl": "156", "pr": "154", "mx": "155"}   # 2026.11.21 등록(아임웹 상품 157 라이트 · 156 플러스 · 154 프로 · 155 맥스)
NAVER_VERIFY = ""
GOOGLE_VERIFY = ""
INDEXNOW_KEY = "7d3f2a9c4b1e48f6a05c9e2d1b7f3a64"
BIZ = {"name": "성균관컨설팅", "ceo": "이채연", "no": "272-32-01885", "ecom": "제2026-경기송탄-0622",
       "addr": "경기도 수원시 장안구 서부로 2066 성균관대학교 브릿지팩토리(연구실)", "mail": "contact@skkc.co.kr"}
# list = 정가(판매가의 2배, 대표 지시 2026.11.21: 가격 · 토큰 정책은 AIMarker 와 같게, 정가를 2배로 적어 50% 할인으로 보이게)
# pg = 검사와 휴머나이징 약 몇 페이지(AIMarker 대표가 정한 값과 같게: 도구 충전 창 humanize.js PRODS 와 맞춤)
PACKS = [
    {"id": "lt", "name": "라이트", "tok": 100, "price": 9900, "list": 19800, "per": "99원", "who": "자기소개서 · 짧은 과제", "chars": "약 8,000자", "pg": "약 5페이지"},
    {"id": "pl", "name": "플러스", "tok": 300, "price": 19900, "list": 39800, "per": "약 66원", "who": "레포트 · 과제 여러 편", "chars": "약 25,000자", "pg": "약 15페이지"},
    {"id": "pr", "name": "프로", "tok": 750, "price": 39900, "list": 79800, "per": "약 53원", "who": "논문 · 학위논문", "chars": "약 62,000자", "pg": "약 40페이지", "best": "BEST 추천", "save": "플러스보다 토큰당 20% 절약"},
    {"id": "mx", "name": "맥스", "tok": 1500, "price": 69900, "list": 139800, "per": "약 47원", "who": "논문 전체 · 여러 편", "chars": "약 125,000자", "pg": "약 100페이지", "top": "최고 혜택", "save": "플러스보다 토큰당 30% 절약"},
]


def esc(s):
    return html.escape(str(s), quote=True)


def ico(name, cls="ico"):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % (cls, ICONS.get(name, ""))


def won(n):
    return "{:,}원".format(n)


def shop(pid):
    ix = SHOP_IDX.get(pid) or ""
    return SHOP % ix if ix else ""


LOGO_SVG = ('<svg viewBox="0 0 40 40" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1730"/><stop offset="1" stop-color="#13254a"/></linearGradient></defs>'
            '<rect width="40" height="40" rx="11" fill="url(#lg)"/><path d="M12 11v18M28 11v18M12 20h16" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>'
            '<circle cx="31.5" cy="31.5" r="5.5" fill="#10b981" stroke="#0b1730" stroke-width="2"/><path d="m29.2 31.6 1.6 1.6 3-3.2" stroke="#fff" stroke-width="1.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')
LOGO = '<a class="logo" href="/" aria-label="%s 홈">%s<span>%s<small>KOREA HUMANIZER</small></span></a>' % (BRAND, LOGO_SVG, BRAND)

NAV = [("ai-humanizer/", "AI 휴머나이저"), ("copykiller/", "카피킬러 AI 작성률"), ("gptkiller/", "GPT킬러"), ("pricing/", "요금"), ("guide/", "가이드"), ("faq/", "자주 묻는 질문")]


def header(path):
    nav = "".join('<a href="/%s"%s>%s</a>' % (p, ' aria-current="page"' if path == p else "", t) for p, t in NAV)
    mnav = "".join('<a href="/%s">%s</a>' % (p, t) for p, t in NAV)
    return ('<header class="hd" id="hd"><div class="wrap hd-in">%s<nav class="nav" aria-label="주요 메뉴">%s</nav>'
            '<div class="hd-r"><a class="btn btn-g btn-s" href="/pricing/">토큰 충전</a><a class="btn btn-p btn-s" href="/#tool" data-tool>%s<span class="hl">무료 AI 작성률 검사</span><span class="hs">무료 검사</span></a>'
            '<button class="menu-btn" id="menuBtn" type="button" aria-label="메뉴 열기" aria-expanded="false" aria-controls="mnav">%s</button></div></div></header>'
            '<nav class="mnav" id="mnav" aria-label="모바일 메뉴">%s<a href="/humanize/">휴머나이징 도구</a><a href="/about/">회사 소개</a></nav>') % (LOGO, nav, ico("search"), ico("menu"), mnav)


def footer():
    cols = [
        ("서비스", [("/humanize/", "휴머나이징 도구"), ("/ai-check/", "AI 작성률 무료 검사"), ("/pricing/", "요금 · 토큰 충전"), ("/faq/", "자주 묻는 질문")]),
        ("많이 찾는 검색", [("/copykiller/", "카피킬러 AI 작성률 낮추기"), ("/gptkiller/", "GPT킬러 낮추기"), ("/ai-humanizer/", "AI 휴머나이저"), ("/lower-ai-rate/", "AI 작성률 낮추기"), ("/ai-bypass/", "AI 탐지 우회"), ("/free/", "AI 휴머나이저 무료")]),
        ("용도별", [("/thesis/", "논문 AI 작성률 낮추기"), ("/resume/", "자기소개서 AI 작성률 낮추기"), ("/natural/", "AI 글 자연스럽게 바꾸기"), ("/guide/", "휴머나이징 가이드")]),
        ("회사 · 정책", [("/about/", "회사 소개"), ("/terms/", "이용약관"), ("/privacy/", "개인정보처리방침"), ("mailto:" + BIZ["mail"], "문의 " + BIZ["mail"])]),
    ]
    c = "".join('<div><h4>%s</h4><ul>%s</ul></div>' % (h, "".join('<li><a href="%s">%s</a></li>' % (u, t) for u, t in L)) for h, L in cols)
    return ('<footer class="ft"><div class="wrap"><div class="ft-top"><div>%s<p>한국어만을 위해 만든 AI 휴머나이저.<br>AI 작성률을 검사하고, 걸리는 문장만 사람 문장으로 바꿉니다.</p></div>%s</div>'
            '<div class="ft-biz"><b>운영</b> %s · 대표 %s · 사업자등록번호 %s · 통신판매업 신고 %s<br>%s · %s<br>'
            '카피킬러, GPT킬러 등은 각 권리자의 상표이며 한국휴머나이저는 해당 서비스와 제휴 관계가 없습니다. AI 작성률과 판정은 한국휴머나이저 판정 기준으로 계산한 값입니다.<br>© 2026 %s. All rights reserved.</div></div></footer>'
            '<div class="mcta" id="mcta"><a class="btn btn-p" href="/#tool" data-tool>%s무료 검사</a><a class="btn btn-g" href="/pricing/">요금 보기</a></div>') % (
        LOGO, c, BIZ["name"], BIZ["ceo"], BIZ["no"], BIZ["ecom"], BIZ["addr"], BIZ["mail"], BRAND, ico("search"))


# ---------------- 구조화 데이터 ----------------
ORG = {"@type": "Organization", "@id": SITE + "/#org", "name": BRAND, "alternateName": [BRAND_EN, "한국 휴머나이저", "humanizer.co.kr"], "url": SITE + "/",
       "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo-512.png", "width": 512, "height": 512},
       "parentOrganization": {"@type": "Organization", "name": BIZ["name"], "taxID": BIZ["no"]},
       "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": BIZ["mail"], "availableLanguage": ["ko"]},
       "address": {"@type": "PostalAddress", "streetAddress": "서부로 2066 성균관대학교 브릿지팩토리", "addressLocality": "수원시 장안구", "addressRegion": "경기도", "postalCode": "16419", "addressCountry": "KR"}}
WEBSITE = {"@type": "WebSite", "@id": SITE + "/#website", "name": BRAND, "alternateName": [BRAND_EN, "한국휴머나이저 AI 휴머나이저"], "url": SITE + "/", "inLanguage": "ko-KR", "publisher": {"@id": SITE + "/#org"}}
APP = {"@type": "WebApplication", "@id": SITE + "/#app", "name": BRAND + " AI 휴머나이저", "url": SITE + "/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Web",
       "inLanguage": "ko-KR", "description": "한국어 AI 작성률 검사와 AI 휴머나이징. 카피킬러 · GPT킬러 같은 AI 탐지기에 걸리는 문장만 골라 사람 문장으로 바꾸고, 같은 기준으로 AI 작성률을 다시 잽니다.",
       "featureList": ["AI 작성률 무료 검사(5만 자)", "문장 단위 AI 검출 표시", "AI 휴머나이징(한국어 전용 엔진)", "한글 HWP · HWPX · 워드 DOCX · PDF 파일 지원", "말투 자동 맞춤", "결과상세내역서 PDF"],
       "offers": {"@type": "AggregateOffer", "priceCurrency": "KRW", "lowPrice": "0", "highPrice": "69900", "offerCount": "5"}, "publisher": {"@id": SITE + "/#org"}}


def ld_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faq]}


def ld_crumbs(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + u} for i, (n, u) in enumerate(trail)]}


def ld_howto(name, steps):
    return {"@type": "HowTo", "name": name, "inLanguage": "ko-KR", "totalTime": "PT2M", "step": [{"@type": "HowToStep", "position": i + 1, "name": a, "text": b} for i, (a, b) in enumerate(steps)]}


def ld_offers():
    return {"@type": "Product", "@id": SITE + "/pricing/#product", "name": BRAND + " 토큰", "brand": {"@type": "Brand", "name": BRAND},
            "description": "AI 작성률 검사와 AI 휴머나이징에 쓰는 토큰. 월 구독 없이 한 번 충전하고, 남은 토큰은 5년 동안 사라지지 않습니다.",
            "image": [SITE + "/assets/product/hz-pr-1x1.jpg", SITE + "/assets/img/og.png"],
            "offers": [{"@type": "Offer", "name": "%s %d토큰" % (p["name"], p["tok"]), "price": str(p["price"]), "priceCurrency": "KRW", "availability": "https://schema.org/InStock",
                        "url": SITE + "/pricing/", "seller": {"@type": "Organization", "name": BIZ["name"]}} for p in PACKS]}


# ---------------- 페이지 틀 ----------------
PAGES = []   # (path, title, desc, lastmod, priority)


def page(path, title, desc, body, *, ld=None, tool=False, og=None, ptype="website", noindex=False, priority="0.7", lastmod=TODAY, extra_head=""):
    url = SITE + "/" + path
    ogimg = og or (SITE + "/assets/img/og.png")
    graph = [ORG, WEBSITE] + (ld or [])
    head = ['<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">',
            '<title>%s</title><meta name="description" content="%s">' % (esc(title), esc(desc)),
            '<link rel="canonical" href="%s">' % url,
            '<meta name="robots" content="%s">' % ("noindex,follow" if noindex else "index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1"),
            '<meta property="og:type" content="%s"><meta property="og:site_name" content="%s"><meta property="og:locale" content="ko_KR">' % (ptype, BRAND),
            '<meta property="og:title" content="%s"><meta property="og:description" content="%s"><meta property="og:url" content="%s">' % (esc(title), esc(desc), url),
            '<meta property="og:image" content="%s"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="%s">' % (ogimg, esc(BRAND + " · AI 작성률 검사와 휴머나이징")),
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="%s"><meta name="twitter:description" content="%s"><meta name="twitter:image" content="%s">' % (esc(title), esc(desc), ogimg),
            '<meta name="theme-color" content="#0b1730"><meta name="format-detection" content="telephone=no">',
            '<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">',
            '<link rel="alternate" type="application/rss+xml" title="%s 가이드" href="/rss.xml">' % BRAND]
    if NAVER_VERIFY:
        head.append('<meta name="naver-site-verification" content="%s">' % NAVER_VERIFY)
    if GOOGLE_VERIFY:
        head.append('<meta name="google-site-verification" content="%s">' % GOOGLE_VERIFY)
    head.append('<script>document.documentElement.className+=" js";setTimeout(function(){if(!window.HZ_SITE){var a=document.querySelectorAll(".rv");for(var i=0;i<a.length;i++)a[i].className+=" in"}},3000)</script>')
    head.append('<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin><link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">')
    if tool:
        head.append('<link rel="stylesheet" href="/assets/tool.css?v=%s">' % VER)
    head.append('<link rel="stylesheet" href="/assets/hz.css?v=%s">' % VER)
    head.append(extra_head)
    head.append('<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")))
    head.append("</head>")
    scripts = ['<script src="/assets/site.js?v=%s" defer></script>' % VER]
    if tool:
        scripts = ['<script>window.HZ_API=%s;</script>' % json.dumps(API),
                   '<script src="/assets/products.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/am.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/textin.js?v=%s" defer></script>' % VER,
                   '<script src="/assets/humanize.js?v=%s" defer></script>' % VER] + scripts
    doc = "".join(head) + '<body data-root="/">' + '<a class="sr" href="#main">본문 바로가기</a>' + header(path) + '<main id="main">' + body + "</main>" + footer() + "".join(scripts) + "</body></html>"
    fp = os.path.join(OUT, path, "index.html") if path else os.path.join(OUT, "index.html")
    if path == "404.html":
        fp = os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(doc)
    if not noindex:
        PAGES.append((path, title, desc, lastmod, priority))


# ---------------- 검사 도구(엔진 화면, humanize.js 가 움직임) ----------------
def tool_html():
    packs = []
    for p in PACKS:
        cls = ' class="best"' if p.get("best") else (' class="top"' if p.get("top") else "")
        tag = '<i class="tg">%s</i>' % p["best"] if p.get("best") else ('<i class="tg top">%s</i>' % p["top"] if p.get("top") else "")
        sv = '<i class="hz17-sv">%s</i>' % p["save"] if p.get("save") else ""
        packs.append('<label%s><input type="radio" name="product" value="%s"%s><span>%s<b class="nm">%s</b><b class="tk">%s<small>토큰</small></b><b class="pr">%s<small>토큰당 %s</small></b>%s<small class="ds">%s · 검사와 휴머나이징 %s</small></span></label>' % (
            cls, p["id"], " checked" if p.get("best") else "", tag, p["name"], "{:,}".format(p["tok"]), won(p["price"]), p["per"], sv, p["who"], p["chars"]))
    return P.TOOL_TPL.format(ico_upload=ico("upload"), ico_search=ico("search"), ico_pen=ico("pen"), ico_lock=ico("lock"), ico_x=ico("x"), ico_spark=ico("sparkle"), ico_arrow=ico("arrow"),
                             packs="".join(packs), biz_no=BIZ["no"], mail=BIZ["mail"])


# ---------------- 예시 화면(실제 엔진 값) ----------------
DEMO = json.load(open(os.path.join(HERE, "demo.json"), encoding="utf-8"))


def tok(s):
    return re.findall(r"\S+\s*", s)


def sent_split(t):
    return [x for x in re.split(r"(?<=[.!?])\s+", t.strip()) if x]


def diff_ops(a, b):
    A, B = tok(a), tok(b)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    ops = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        x, y = "".join(A[i1:i2]), "".join(B[j1:j2])
        ops.append(("e", x, x) if op == "equal" else ("c", x, y))
    return ops


def _chg(x, y, mode):
    """mode: anim(예시 화면, 바뀔 말에 새 말을 data-n 으로) · src(원문) · dst(다듬은 글)"""
    sx, sy = x.rstrip(), y.rstrip()
    tx, ty = x[len(sx):], y[len(sy):]
    if mode == "src":
        return ('<span class="x">%s</span>%s' % (esc(sx), esc(tx))) if sx else ""
    if mode == "dst":
        return ('<mark>%s</mark>%s' % (esc(sy), esc(ty))) if sy else ""
    return '<span class="x" data-n="%s">%s</span>%s' % (esc(sy + ty), esc(sx), esc(tx)) if (sx or sy) else ""


def _sent_ops(src, dst):
    """원문 문장마다 [(종류, 원래 말, 바뀐 말)] 목록. 휴머나이징이 문장을 잇거나 나눠도 원문 문장 경계로 자름"""
    A, B = tok(src), tok(dst)
    sid, k = [], 0
    for t in A:
        sid.append(k)
        if re.search(r"[.!?]\s*$", t):
            k += 1
    n = (sid[-1] + 1) if sid else 0
    per = [[] for _ in range(n)]
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        y = "".join(B[j1:j2])
        if i1 == i2:   # 넣기만 한 말: 앞 문장 끝에 붙임
            tgt = sid[i1 - 1] if i1 > 0 else 0
            per[tgt].append(("c", "", y))
            continue
        segs = []
        for i in range(i1, i2):
            if not segs or segs[-1][0] != sid[i]:
                segs.append([sid[i], []])
            segs[-1][1].append(A[i])
        for m, (si, toks) in enumerate(segs):
            x = "".join(toks)
            if op == "equal":
                per[si].append(("e", x, x))
            else:
                per[si].append(("c", x, y if m == 0 else ""))
    return per


def demo_samples():
    out = []
    for S in DEMO["samples"]:
        flags, scores = set(S.get("ai", [])), S.get("scores", {})
        bs, as_ = sent_split(S["src"]), sent_split(S["dst"])
        same = len(bs) == len(as_)
        ascores = S.get("after_scores", {}) if same else {}
        per = _sent_ops(S["src"], S["dst"])
        anim, src, dst, nch = [], [], [], 0
        for i, ops in enumerate(per):
            n = sum(1 for o in ops if o[0] == "c")
            nch += n
            isai = i in flags
            p0, p1 = scores.get(str(i)), ascores.get(str(i))
            tag = ('<i class="demo-tag" data-p1="%s">AI %s%%</i>' % ("" if p1 is None else p1, p0)) if (isai and p0 is not None) else ""
            A_ = "".join(esc(o[1]) if o[0] == "e" else _chg(o[1], o[2], "anim") for o in ops)
            S_ = "".join(esc(o[1]) if o[0] == "e" else _chg(o[1], o[2], "src") for o in ops)
            D_ = "".join(esc(o[2]) if o[0] == "e" else _chg(o[1], o[2], "dst") for o in ops)
            anim.append('<span class="s%s">%s%s</span> ' % (" ai" if isai else "", A_.rstrip(), tag))
            src.append('<span class="s%s">%s%s</span> ' % (" ai" if isai else "", S_.rstrip(), tag.replace("demo-tag", "demo-tag st")))
            dst.append('<span class="s%s">%s</span> ' % (" hu" if n else "", D_.rstrip()))
        out.append({"k": S["k"], "label": S["label"], "file": S["file"], "before": S["before"], "after": S["after"], "changes": nch,
                    "doc": '<p class="ai-blk">' + "".join(anim).strip() + "</p>",
                    "src": '<p class="ai-blk">' + "".join(src).strip() + "</p>", "dst": '<p class="hu-blk">' + "".join(dst).strip() + "</p>"})
    return out


def demo_json():
    return '<script type="application/json" id="hzDemoData">%s</script>' % json.dumps({"samples": demo_samples(), "measured": DEMO["measured"]}, ensure_ascii=False).replace("</", "<\\/")


def demo_card():
    S = demo_samples()
    tabs = "".join('<button type="button" role="tab" aria-selected="%s">%s</button>' % ("true" if i == 0 else "false", s["label"]) for i, s in enumerate(S))
    first = S[0]
    return ('<div class="demo" id="demo" aria-label="AI 작성률 검사와 휴머나이징 예시(실제 엔진 값)">'
            '<div class="demo-bar"><i></i><i></i><i></i><span class="fn">%s<span>%s</span></span><div class="demo-tabs" role="tablist" aria-label="예시 글 종류">%s</div></div>'
            '<div class="demo-scan" aria-hidden="true"></div>'
            '<div class="demo-meter"><div class="dm from bad"><small>휴머나이징 전 · AI작성률</small><b>%s<small style="font-size:18px">%%</small> <em>%s</em></b><div class="dm-bar"><i style="width:%s%%"></i></div></div>'
            '<span class="dm-arr" aria-hidden="true">%s</span>'
            '<div class="dm to good wait"><small>휴머나이징 후 · AI작성률</small><b>– <em>대기</em></b><div class="dm-bar"><i style="width:0"></i></div></div></div>'
            '<div class="demo-legend"><span class="a"><i></i>AI 작성률 검출 문장</span><span class="h"><i></i>사람 문장으로 바꾼 곳</span><span class="demo-state" aria-live="polite"></span></div>'
            '<div class="demo-doc">%s</div>'
            '<div class="demo-ft"><button class="btn btn-p btn-s" type="button" data-demo-run data-run="%s휴머나이징 보기" data-again="%s처음부터 다시">%s휴머나이징 보기</button>'
            '<a class="btn btn-g btn-s" href="#tool" data-tool>내 글로 해 보기</a><span class="note">%s</span></div></div>') % (
        ico("file"), esc(first["file"]), tabs, first["before"]["rate"], first["before"]["band"], first["before"]["rate"], ico("arrow"),
        first["doc"], esc(ico("sparkle")), esc(ico("refresh")), ico("sparkle"), esc(DEMO["measured"]))


def compare_block():
    S = demo_samples()
    tabs = "".join('<button type="button" role="tab" aria-selected="%s">%s</button>' % ("true" if i == 0 else "false", s["label"]) for i, s in enumerate(S))
    return ('<div class="cmp-tabs" role="tablist" aria-label="예시 글 종류">%s</div><div class="cmp" id="cmp">'
            '<div class="cmp-col"><div class="cmp-h"><span>휴머나이징 전</span><span class="pill l bad"></span></div><div class="cmp-t l"></div></div>'
            '<div class="cmp-col"><div class="cmp-h"><span>휴머나이징 후</span><span class="pill r good"></span></div><div class="cmp-t r"></div></div></div>'
            '<div class="cmp-foot"></div><p class="center" style="font-size:13px;color:var(--ink-3);margin-top:10px">%s</p>') % (tabs, esc(DEMO["measured"]))


def faq_html(faq):
    return '<div class="faq">' + "".join('<details><summary>%s</summary><div class="a"><p>%s</p></div></details>' % (esc(q), a) for q, a in faq) + "</div>"


def pricing_cards(cta_text="구매하기"):
    out = []
    for p in PACKS:
        cls = "pk best" if p.get("best") else "pk"
        tag = '<span class="tg">%s</span>' % p["best"] if p.get("best") else ('<span class="tg top">%s</span>' % p["top"] if p.get("top") else "")
        link = shop(p["id"])
        btn = ('<a class="btn %s" href="%s" target="_blank" rel="noopener" data-pack="%s">%s %s</a>' % ("btn-p" if p.get("best") else "btn-d", esc(link), p["id"], cta_text, ico("arrow"))) if link else \
              ('<a class="btn %s" href="/humanize/#buy-%s">%s %s</a>' % ("btn-p" if p.get("best") else "btn-d", p["id"], cta_text, ico("arrow")))
        feats = ["AI 작성률 검사와 휴머나이징 " + p["chars"] + "(" + p["pg"] + ")", "모든 문장 AI 표시 · 판정 근거", "결과상세내역서 PDF · 파일 그대로 받기", "남은 토큰 5년 동안 유지"]
        lp = ('<p class="lp"><s>정가 %s</s><b>50%%</b></p>' % won(p["list"])) if p.get("list") else ""
        out.append('<div class="%s rv">%s<h3>%s</h3><p class="who">%s</p><p class="tk">%s토큰</p>%s<p class="pr">%s</p><p class="per">토큰당 %s · 부가세 포함</p>%s<ul>%s</ul>%s</div>' % (
            cls, tag, p["name"], p["who"], "{:,}".format(p["tok"]), lp, won(p["price"]), p["per"], ('<span class="sv">%s</span>' % p["save"]) if p.get("save") else "",
            "".join("<li>%s%s</li>" % (ico("check"), f) for f in feats), btn))
    return '<div class="price">' + "".join(out) + "</div>"


def cta_band(h="제출 버튼을 누르기 전, 30초면 충분합니다", p="지금 가진 글의 AI 작성률부터 무료로 확인하세요. 가입도, 카드 등록도 필요 없습니다."):
    return ('<section class="sec-s"><div class="wrap"><div class="cta rv"><h2>%s</h2><p>%s</p><div class="btns"><a class="btn btn-p btn-l" href="/#tool" data-tool>%s무료로 AI 작성률 검사</a>'
            '<a class="btn btn-g btn-l" href="/pricing/">요금 보기</a></div></div></div></section>') % (h, p, ico("search"))


def crumbs_html(trail):
    return '<nav class="crumb" aria-label="현재 위치"><a href="/">홈</a>' + "".join('<span>›</span>' + ('<a href="/%s">%s</a>' % (u, esc(n)) if i < len(trail) - 1 else '<span>%s</span>' % esc(n)) for i, (n, u) in enumerate(trail)) + "</nav>"


def hero_with_tool(eyebrow, h1, lead, pts=None, cls="hero"):
    pts = pts or ["한국어 전용 엔진", "문장 단위 AI 작성률", "한글 · 워드 · PDF 그대로", "글은 저장하지 않음"]
    return ('<section class="%s" id="top"><div class="wrap"><div class="hero-grid"><div id="tool" class="tool-w"><p class="eyebrow">%s</p><h1 class="h1">%s</h1><p class="lead">%s</p>'
            '<ul class="hero-pts">%s</ul>%s</div><div>%s</div></div></div></section>') % (
        cls, eyebrow, h1, lead, "".join("<li>%s%s</li>" % (ico("check"), t) for t in pts), tool_html(), demo_card())


# ---------------- 홈 ----------------
def build_home():
    H = P.HOME
    body = hero_with_tool(H["eyebrow"], H["h1"], H["lead"])
    body += demo_json()
    body += P.trust_strip(ico)
    body += P.alarm_section(ico)
    body += ('<section class="sec" id="example"><div class="wrap"><div class="center"><p class="kick">%s실제 엔진으로 잰 결과</p><h2 class="h2">보라색 문장이 사라질 때까지,<br>뜻은 그대로 두고 말투만 사람처럼</h2>'
             '<p class="sub">아래 예시는 한국휴머나이저 엔진에 그대로 넣어 잰 실제 값입니다. 보라색은 AI로 검출된 문장, 초록색은 사람 문장으로 바꾼 곳입니다.</p></div>%s</div></section>') % (ico("eye"), compare_block())
    body += P.how_section(ico)
    body += P.features_section(ico)
    body += P.compare_table(ico)
    body += P.usecases_section(ico)
    body += ('<section class="sec alt" id="price"><div class="wrap"><div class="center"><p class="kick">%s요금</p><h2 class="h2">월 구독 없이, 쓴 만큼만</h2><p class="sub">한 번 충전하면 글자 수만큼만 빠지고, 남은 토큰은 5년 동안 사라지지 않습니다. 검사는 언제나 무료로 먼저 해 보세요.</p></div>%s'
             '<p class="price-note">AI 작성률 검사 1,000자 4토큰 · AI 휴머나이징 1,000자 8토큰 · 1토큰 100원 · 결제는 운영사 성균관컨설팅 결제 페이지(가입 없이 카드 · 간편결제)</p></div></section>') % (ico("card"), pricing_cards())
    body += '<section class="sec" id="faq"><div class="wrap-n"><div class="center"><p class="kick">%s자주 묻는 질문</p><h2 class="h2">궁금한 점, 먼저 답해 드립니다</h2></div>%s</div></section>' % (ico("chat"), faq_html(H["faq"]))
    body += cta_band()
    ld = [APP, ld_faq(H["faq"]), ld_howto("AI 작성률 낮추기(한국휴머나이저)", P.HOW_STEPS)]
    page("", H["title"], H["desc"], body, ld=ld, tool=True, priority="1.0")


def build_humanize():
    body = hero_with_tool('<b>도구</b> AI 작성률 검사 · 휴머나이징', 'AI 휴머나이징 도구', '글을 붙여 넣거나 파일을 올리면 AI 작성률부터 무료로 보여 드립니다. 걸리는 문장은 휴머나이징으로 사람 문장으로 바꾸고, 같은 기준으로 다시 잽니다.', cls="hero lp-hero")
    body += demo_json() + P.how_section(ico) + cta_band()
    page("humanize/", "AI 휴머나이징 도구 · AI 작성률 검사 | " + BRAND, "한국휴머나이저 AI 휴머나이징 도구. 글이나 한글 · 워드 · PDF 파일을 넣으면 AI 작성률과 AI로 검출된 문장을 보여 주고, 사람 문장으로 바꿔 드립니다.",
         body, ld=[APP, ld_crumbs([("휴머나이징 도구", "humanize/")])], tool=True, priority="0.9")


def build_pricing():
    trail = [("요금", "pricing/")]
    body = ('<section class="ph"><div class="wrap">%s<h1 class="h1">요금 · 토큰 충전</h1><p class="lead">지금 모든 토큰이 정가의 <b>50%%</b> 가격입니다. 월 구독 없이 한 번 충전하고 쓴 만큼만, 남은 토큰은 5년 동안 사라지지 않습니다.</p></div></section>'
            '<section class="sec-s"><div class="wrap">%s<p class="price-note">결제는 운영사 성균관컨설팅 결제 페이지에서 가입 없이 카드 · 간편결제로 합니다. 결제하면 보통 1분 안에, 적은 이메일로 16자리 토큰 코드가 갑니다.</p></div></section>') % (crumbs_html(trail), pricing_cards())
    body += P.pricing_detail(ico)
    body += '<section class="sec alt"><div class="wrap-n"><h2 class="h2 center">결제 · 토큰 자주 묻는 질문</h2>%s</div></section>' % faq_html(P.PRICE_FAQ)
    body += cta_band("먼저 무료로 검사해 보세요", "AI 작성률이 높게 나온 문장만 휴머나이징하면 토큰을 아낄 수 있습니다.")
    page("pricing/", "요금 · 토큰 충전 | " + BRAND + " AI 휴머나이저", "한국휴머나이저 요금. 정가의 50% 가격으로 라이트 100토큰 9,900원부터 맥스 1,500토큰 69,900원까지. 월 구독 없이 한 번 충전, AI 작성률 검사 1,000자 4토큰 · 휴머나이징 1,000자 8토큰.",
         body, ld=[ld_offers(), ld_faq(P.PRICE_FAQ), ld_crumbs(trail)], priority="0.9")


def build_faq():
    trail = [("자주 묻는 질문", "faq/")]
    allq = P.HOME["faq"] + P.PRICE_FAQ + P.MORE_FAQ
    body = '<section class="ph"><div class="wrap">%s<h1 class="h1">자주 묻는 질문</h1><p class="lead">AI 휴머나이저, AI 작성률, 카피킬러 · GPT킬러, 결제와 토큰에 대해 자주 받는 질문을 모았습니다.</p></div></section>' % crumbs_html(trail)
    body += '<section class="sec-s"><div class="wrap-n">%s</div></section>' % faq_html(allq)
    body += cta_band()
    page("faq/", "자주 묻는 질문 · AI 휴머나이저 FAQ | " + BRAND, "AI 휴머나이저가 무엇인지, 카피킬러 AI 작성률을 낮출 수 있는지, 무료인지, 글이 저장되는지, 결제와 토큰은 어떻게 되는지 답해 드립니다.",
         body, ld=[ld_faq(allq), ld_crumbs(trail)], priority="0.8")


def build_landings():
    for L in P.LANDINGS:
        trail = [(L["crumb"], L["path"])]
        body = hero_with_tool(L["eyebrow"], L["h1"], L["lead"], L.get("pts"), cls="hero lp-hero")
        body += demo_json()
        body += '<section class="sec-s"><div class="wrap-n">%s<div class="answer">%s</div><div class="prose">%s</div></div></section>' % (crumbs_html(trail), L["answer"], L["body"])
        body += ('<section class="sec alt"><div class="wrap"><div class="center"><p class="kick">%s실제 엔진으로 잰 결과</p><h2 class="h2">%s</h2><p class="sub">보라색은 AI로 검출된 문장, 초록색은 사람 문장으로 바꾼 곳입니다.</p></div>%s</div></section>') % (ico("eye"), L.get("cmp_h", "휴머나이징 전과 후, 직접 비교해 보세요"), compare_block())
        body += P.how_section(ico)
        body += '<section class="sec"><div class="wrap-n"><h2 class="h2 center">%s 자주 묻는 질문</h2>%s<div class="links" style="margin-top:28px;justify-content:center">%s</div></div></section>' % (
            esc(L["crumb"]), faq_html(L["faq"]), "".join('<a href="/%s">%s</a>' % (u, t) for u, t in L["related"]))
        body += '<section class="sec-s alt"><div class="wrap"><div class="center"><h2 class="h2">요금</h2></div>%s</div></section>' % pricing_cards()
        body += cta_band()
        page(L["path"], L["title"], L["desc"], body, ld=[APP, ld_faq(L["faq"]), ld_crumbs(trail), ld_howto(L["h1t"], P.HOW_STEPS)], tool=True, priority=L.get("prio", "0.9"))


def build_guides():
    trail0 = [("가이드", "guide/")]
    cards = "".join('<a class="gcard rv" href="/guide/%s/"><small>%s</small><h3>%s</h3><p>%s</p></a>' % (g["slug"], g["cat"], esc(g["h1"]), esc(g["desc"])) for g in P.GUIDES)
    body = ('<section class="ph"><div class="wrap">%s<h1 class="h1">휴머나이징 가이드</h1><p class="lead">카피킬러 · GPT킬러가 무엇을 보고 AI 작성률을 매기는지, 어떻게 하면 AI 티가 나지 않는 글이 되는지 정리했습니다.</p></div></section>'
            '<section class="sec-s"><div class="wrap"><div class="gcards">%s</div></div></section>') % (crumbs_html(trail0), cards)
    body += cta_band()
    page("guide/", "휴머나이징 가이드 · AI 작성률 낮추는 법 | " + BRAND, "카피킬러 AI 작성률 0%와 20% 미만, GPT킬러 안 걸리는 법, AI 탐지기 원리, AI 패턴 8가지, 챗GPT 티 안 나게 쓰는 법까지 정리한 휴머나이징 가이드.",
         body, ld=[ld_crumbs(trail0), {"@type": "CollectionPage", "name": BRAND + " 휴머나이징 가이드", "url": SITE + "/guide/"}], priority="0.8")
    for g in P.GUIDES:
        trail = [("가이드", "guide/"), (g["h1"], "guide/%s/" % g["slug"])]
        toc = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', g["body"])
        toc_html = ('<nav class="toc" aria-label="목차"><b>목차</b><ol>%s</ol></nav>' % "".join('<li><a href="#%s">%s</a></li>' % (i, t) for i, t in toc)) if toc else ""
        others = [o for o in P.GUIDES if o["slug"] != g["slug"]][:3]
        rel = "".join('<a class="gcard" href="/guide/%s/"><small>%s</small><h3>%s</h3><p>%s</p></a>' % (o["slug"], o["cat"], esc(o["h1"]), esc(o["desc"])) for o in others)
        body = ('<article><section class="ph"><div class="wrap-n">%s<p class="kick">%s</p><h1 class="h1">%s</h1><p class="meta"><span>%s 편집팀</span><span>%s</span><span>읽는 데 %d분</span></p></div></section>'
                '<section class="sec-s"><div class="wrap-n"><div class="answer">%s</div>%s<div class="prose">%s</div>'
                '<div class="cta" style="margin-top:40px;padding:36px 24px"><h2 style="font-size:26px">내 글의 AI 작성률, 지금 바로 확인하세요</h2><p>가입 없이 무료 · 문장마다 AI 검출 여부를 보여 드립니다.</p><div class="btns"><a class="btn btn-p btn-l" href="/humanize/">무료로 AI 작성률 검사</a></div></div>'
                '</div></section></article><section class="sec-s alt"><div class="wrap"><h2 class="h2">함께 읽으면 좋은 글</h2><div class="gcards">%s</div></div></section>') % (
            crumbs_html(trail), g["cat"], esc(g["h1"]), BRAND, g["date"].replace("-", "."), max(2, len(re.sub(r"<[^>]+>", "", g["body"])) // 650), g["answer"], toc_html, g["body"], rel)
        art = {"@type": "Article", "headline": g["h1"], "description": g["desc"], "inLanguage": "ko-KR", "datePublished": g["date"], "dateModified": g["date"],
               "author": {"@type": "Organization", "name": BRAND + " 편집팀", "url": SITE + "/about/"}, "publisher": {"@id": SITE + "/#org"},
               "mainEntityOfPage": SITE + "/guide/%s/" % g["slug"], "image": [SITE + "/assets/product/hz-pr-1x1.jpg", SITE + "/assets/img/og.png"], "articleSection": g["cat"]}
        ld = [art, ld_crumbs(trail)] + ([ld_faq(g["faq"])] if g.get("faq") else [])
        page("guide/%s/" % g["slug"], g["title"], g["desc"], body, ld=ld, ptype="article", priority="0.7", lastmod=g["date"],
             extra_head='<meta property="article:published_time" content="%sT09:00:00+09:00">' % g["date"])


def build_static():
    for S in P.STATIC:
        trail = [(S["crumb"], S["path"])]
        body = '<section class="ph"><div class="wrap-n">%s<h1 class="h1">%s</h1>%s</div></section><section class="sec-s"><div class="wrap-n prose">%s</div></section>' % (
            crumbs_html(trail), S["h1"], ('<p class="lead">%s</p>' % S["lead"]) if S.get("lead") else "", S["body"])
        page(S["path"], S["title"], S["desc"], body, ld=[ld_crumbs(trail)], priority=S.get("prio", "0.4"))
    body = '<section class="ph"><div class="wrap-n"><h1 class="h1">페이지를 찾을 수 없습니다</h1><p class="lead">주소가 바뀌었거나 없는 페이지입니다.</p><p><a class="btn btn-p" href="/">홈으로</a> <a class="btn btn-g" href="/humanize/">휴머나이징 도구</a></p></div></section>'
    page("404.html", "페이지를 찾을 수 없습니다 | " + BRAND, "요청한 페이지를 찾을 수 없습니다.", body, noindex=True)


# ---------------- 검색 · AI 검색용 파일 ----------------
def build_seo():
    urls = []
    for path, title, desc, lastmod, pr in PAGES:
        urls.append("<url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>" % (SITE, path, lastmod, "weekly" if pr >= "0.8" else "monthly", pr))
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + "\n</urlset>\n")
    bots = ["Googlebot", "Yeti", "Daum", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended", "CCBot", "Meta-ExternalAgent", "cohere-ai", "DuckAssistBot", "MistralAI-User"]
    rob = "# %s · 검색 엔진과 AI 검색이 모두 읽을 수 있게 엽니다\n" % BRAND + "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots) + "User-agent: *\nAllow: /\nDisallow: /assets/vendor/\n\nSitemap: %s/sitemap.xml\n" % SITE
    open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8").write(rob)
    open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8").write(P.llms_txt(SITE, PAGES, PACKS))
    open(os.path.join(OUT, "llms-full.txt"), "w", encoding="utf-8").write(P.llms_full(SITE, PACKS))
    items = "".join("<item><title>%s</title><link>%s/guide/%s/</link><guid>%s/guide/%s/</guid><pubDate>%s</pubDate><description>%s</description></item>" % (
        esc(g["h1"]), SITE, g["slug"], SITE, g["slug"], datetime.datetime.strptime(g["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900"), esc(g["desc"])) for g in P.GUIDES)
    open(os.path.join(OUT, "rss.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>%s 가이드</title><link>%s/guide/</link><description>AI 작성률 낮추기와 휴머나이징 가이드</description><language>ko</language>%s</channel></rss>' % (BRAND, SITE, items))
    open(os.path.join(OUT, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps({"name": BRAND + " AI 휴머나이저", "short_name": BRAND, "start_url": "/", "display": "standalone", "background_color": "#ffffff", "theme_color": "#0b1730", "lang": "ko",
                                                                                         "icons": [{"src": "/assets/img/logo-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/img/logo-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))
    open(os.path.join(OUT, INDEXNOW_KEY + ".txt"), "w").write(INDEXNOW_KEY)
    open(os.path.join(OUT, "CNAME"), "w").write("humanizer.co.kr\n")
    open(os.path.join(OUT, ".nojekyll"), "w").write("\n")
    prods = {"shop": SHOP, "idx": {k: v for k, v in SHOP_IDX.items()}, "items": {p["id"]: {"name": p["name"], "tok": p["tok"], "price": p["price"], "list": p.get("list", 0)} for p in PACKS}}
    open(os.path.join(OUT, "assets", "products.js"), "w", encoding="utf-8").write("/* %s 상품(빌드가 만듦: _src/build.py SHOP_IDX · PACKS) */\nwindow.AMP = %s;\n" % (BRAND, json.dumps(prods, ensure_ascii=False)))


def verify():
    bad = []
    for dp, dn, fn in os.walk(OUT):
        if "/assets" in dp:
            continue
        for f in fn:
            if not f.endswith((".html", ".txt", ".xml")):
                continue
            s = open(os.path.join(dp, f), encoding="utf-8").read()
            if "—" in s:
                bad.append("줄표(—) " + os.path.join(dp, f))
            for m in re.finditer(r'href="(/[^"#?]*)', s):
                u = m.group(1)
                if u.startswith("/assets/") or u.endswith((".png", ".svg", ".ico", ".xml", ".webmanifest", ".txt")):
                    continue
                t = os.path.join(OUT, u.lstrip("/"), "index.html") if u.endswith("/") else os.path.join(OUT, u.lstrip("/"))
                if not os.path.exists(t):
                    bad.append("링크 " + u + " in " + f)
            for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
                try:
                    json.loads(m.group(1))
                except Exception as e:
                    bad.append("JSON-LD " + f + " " + str(e))
    return sorted(set(bad))


if __name__ == "__main__":
    build_home()
    build_humanize()
    build_pricing()
    build_faq()
    build_landings()
    build_guides()
    build_static()
    build_seo()
    problems = verify()
    print("pages", len(PAGES), "problems", len(problems))
    for p in problems[:40]:
        print(" -", p)
