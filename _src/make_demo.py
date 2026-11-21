# -*- coding: utf-8 -*-
"""엔진 실측(HZB 줄)을 예시 화면 데이터(demo.json)로. python3 _src/make_demo.py"""
import json, os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
META = {"t6": ("논문", "학위논문_결론.hwp"), "report": ("대학 레포트", "기후변화_레포트.docx"), "t3": ("자기소개서", "자기소개서_지원동기.docx"), "t5": ("블로그 글", "블로그_원고.txt")}
ORDER = ["t6", "report", "t3", "t5"]
raw = {}
for fp in glob.glob(os.path.join(HERE, "demo_raw_*.json")):
    o = json.load(open(fp, encoding="utf-8")); raw[o["k"]] = o
out = []
for k in ORDER:
    if k not in raw: continue
    o = raw[k]
    out.append({"k": k, "label": META[k][0], "file": META[k][1], "src": o["src"], "dst": o["dst"],
                "ai": [i for i, s in enumerate(o["sc"]) if s[1]], "scores": {str(i): s[0] for i, s in enumerate(o["sc"]) if s[1]},
                "after_scores": {str(i): s[0] for i, s in enumerate(o.get("afterSc", []))},
                "before": {"rate": o["before"]["rate"], "band": o["before"]["band"], "n": o["before"]["n"]},
                "after": {"rate": o["after"]["rate"], "band": o["after"]["band"], "n": o["after"]["n"]}, "applied": o.get("ch", 0)})
json.dump({"samples": out, "measured": "2026.11.21 한국휴머나이저 엔진 실측값(판정 기준 1.6 · 인간화 엔진 HUM 2.5, 한 번의 휴머나이징). 글마다 결과는 다릅니다."},
          open(os.path.join(HERE, "demo.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("samples", [s["k"] for s in out])
