"""Render carousel slides from a content JSON file into JPEGs (1080x1350).

Usage:
  python render.py content/week1.json posts            # render JPEGs (needs playwright + chromium)
  python render.py content/week1.json --preview out.html  # one HTML page with every slide, for review

Slides may carry "img": an https URL of an illustration (cover: 4:5, point: 3:2).
Creates posts/<date>/01.jpg ... and posts/<date>/caption.txt. Existing posted folders are skipped.
"""
import html
import json
import sys
from pathlib import Path

W, H = 1080, 1350
RED = "#D12523"
RED_DARK = "#A91C1B"
CREAM = "#FFF5EA"
NAVY = "#16203A"
FONT_DIR = Path(__file__).parent / "fonts"
ASSET_DIR = Path(__file__).parent / "assets"
LOGO_K = (ASSET_DIR / "logo_k.png").resolve().as_uri()
LOGO_WORD = (ASSET_DIR / "logo_word.png").resolve().as_uri()

GOOGLE_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Kanit:wght@600;800&family=Sarabun:wght@400;600&family=Mali:ital,wght@1,700&display=block" rel="stylesheet">'


def local_fonts():
    faces = [("Kanit", 800, "normal", "Kanit-ExtraBold"), ("Kanit", 600, "normal", "Kanit-SemiBold"),
             ("Sarabun", 400, "normal", "Sarabun-Regular"), ("Sarabun", 600, "normal", "Sarabun-SemiBold"),
             ("Mali", 700, "italic", "Mali-BoldItalic")]
    return "<style>" + "".join(
        f"@font-face{{font-family:'{f}';font-weight:{w};font-style:{s};src:url('{(FONT_DIR / (n + '.ttf')).resolve().as_uri()}')}}"
        for f, w, s, n in faces) + "</style>"


BASE_CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
.slide {{ position:relative; width:{W}px; height:{H}px; overflow:hidden; font-family:'Sarabun'; }}
.logo {{ width:132px; height:132px; border-radius:50%; background:{RED}; color:#fff;
  display:flex; align-items:center; justify-content:center;
  font-family:'Mali'; font-weight:700; font-style:italic; font-size:30px; letter-spacing:-0.5px; }}
.logo.inv {{ background:#fff; color:{RED}; }}
.footer {{ position:absolute; left:80px; right:80px; bottom:60px; display:flex;
  align-items:center; justify-content:space-between; font-family:'Kanit'; font-weight:600; font-size:28px; }}
.dots {{ display:flex; gap:12px; }}
.dot {{ width:14px; height:14px; border-radius:50%; background:currentColor; opacity:.3; }}
.dot.on {{ opacity:1; width:40px; border-radius:7px; }}
"""


def esc(s):
    return html.escape(s).replace("\n", "<br>")


def dots(i, n):
    return "".join(f'<div class="dot{" on" if k == i else ""}"></div>' for k in range(n))


def cover(s, i, n):
    if s.get("img"):
        bg = f"""<img src="{html.escape(s['img'])}" style="position:absolute; inset:0; width:100%; height:100%; object-fit:cover;">
  <div style="position:absolute; left:0; right:0; bottom:0; height:62%; background:linear-gradient(to top, {RED} 0%, {RED} 55%, rgba(209,37,35,0) 100%);"></div>"""
        top = 640
        size = 100
    else:
        bg = f"""<div style="position:absolute; width:1100px; height:1100px; border-radius:50%; background:{RED_DARK}; right:-520px; top:-420px;"></div>"""
        top, size = 330, 118
    return f"""
<div class="slide" style="background:{RED}; color:#fff;">
  {bg}
  <img src="{LOGO_K}" style="position:absolute; left:80px; top:80px; width:150px; height:150px; border-radius:50%; border:6px solid #fff; box-sizing:border-box;">
  <div style="position:absolute; left:80px; right:80px; top:{top}px;">
    <div style="display:inline-block; background:{CREAM}; color:{RED}; font-family:'Kanit'; font-weight:600; font-size:34px; padding:8px 28px; border-radius:40px;">{esc(s['kicker'])}</div>
    <div style="font-family:'Kanit'; font-weight:800; font-size:{size}px; line-height:1.16; margin-top:26px; text-shadow:0 2px 12px rgba(0,0,0,.12);">{esc(s['title'])}</div>
    <div style="font-family:'Kanit'; font-weight:600; font-size:38px; margin-top:26px; opacity:.95;">{esc(s['sub'])}</div>
  </div>
  <div class="footer" style="color:#fff;"><span>@KingcrabFrozen</span><div class="dots">{dots(i, n)}</div></div>
</div>"""


def point(s, i, n):
    body = esc(s["body"])
    has_img = bool(s.get("img"))
    img = (f"""<div style="position:absolute; left:0; right:0; top:0; height:660px; overflow:hidden;">
    <img src="{html.escape(s['img'])}" style="width:100%; height:100%; object-fit:cover;"></div>""" if has_img else "")
    top = 585 if has_img else 200
    title_size, body_size = (74, 46) if has_img else (88, 52)
    header = "" if has_img else f"""<div style="position:absolute; left:80px; top:80px; display:flex; align-items:center; gap:22px;">
    <img src="{LOGO_K}" style="width:100px; height:100px; border-radius:50%;">
    <span style="font-family:'Kanit'; font-weight:600; font-size:28px; color:{RED};">Kingcrab Frozen</span></div>"""
    justify = "flex-start" if has_img else "center"
    return f"""
<div class="slide" style="background:{CREAM}; color:{NAVY};">
  {img}{header}
  <div style="position:absolute; left:80px; right:80px; top:{top}px; bottom:140px; display:flex; flex-direction:column; justify-content:{justify};">
    <div style="display:flex; align-items:center; gap:26px;">
      <div style="width:150px; height:150px; border-radius:50%; background:{RED}; color:#fff; display:flex; align-items:center; justify-content:center; font-family:'Kanit'; font-weight:800; font-size:80px; border:8px solid {CREAM};">{esc(s['n'])}</div>
      <div style="font-family:'Kanit'; font-weight:600; font-size:34px; color:{RED}; background:{CREAM}; border:3px solid {RED}; padding:4px 24px; border-radius:40px; margin-top:{60 if has_img else 0}px;">{esc(s['tag'])}</div>
    </div>
    <div style="font-family:'Kanit'; font-weight:800; font-size:{title_size}px; line-height:1.22; margin-top:20px;">{esc(s['title'])}</div>
    <div style="width:110px; height:8px; background:{RED}; border-radius:4px; margin:26px 0;"></div>
    <div style="font-family:'Sarabun'; font-size:{body_size}px; line-height:1.55;">{body}</div>
  </div>
  <div class="footer" style="color:{NAVY};"><span>@KingcrabFrozen</span><div class="dots" style="color:{RED};">{dots(i, n)}</div></div>
</div>"""


def cta(s, i, n):
    return f"""
<div class="slide" style="background:{NAVY}; color:#fff;">
  <div style="position:absolute; width:900px; height:900px; border-radius:50%; background:{RED}; left:-300px; bottom:-480px; opacity:.9;"></div>
  <img src="{LOGO_WORD}" style="position:absolute; left:50%; top:90px; transform:translateX(-50%); width:480px; border-radius:36px;">
  <div style="position:absolute; left:80px; right:80px; top:400px; text-align:center;">
    <div style="font-family:'Kanit'; font-weight:800; font-size:100px; line-height:1.2;">{esc(s['title'])}</div>
    <div style="font-family:'Sarabun'; font-weight:600; font-size:44px; line-height:1.5; margin-top:44px; opacity:.9;">{esc(s['body'])}</div>
    <div style="display:inline-block; margin-top:60px; background:#fff; color:{RED}; font-family:'Kanit'; font-weight:600; font-size:40px; padding:22px 48px; border-radius:60px;">{esc(s['action'])}</div>
  </div>
  <div class="footer" style="color:#fff;"><span>@KingcrabFrozen</span><div class="dots">{dots(i, n)}</div></div>
</div>"""


RENDER = {"cover": cover, "point": point, "cta": cta}


def slide_doc(s, i, n, fonts):
    return (f"<!doctype html><html><head><meta charset='utf-8'>{fonts}<style>{BASE_CSS} body{{width:{W}px;height:{H}px;overflow:hidden}}</style>"
            f"</head><body>{RENDER[s['type']](s, i, n)}</body></html>")


def preview(days, out_html):
    scale = 0.3
    secs = []
    for k, day in enumerate(days):
        n = len(day["slides"])
        cells = "".join(
            f'<div class="cell"><div class="sc">{RENDER[s["type"]](s, i, n)}</div></div>' for i, s in enumerate(day["slides"]))
        secs.append(f'<section><h2>วันที่ {k + 1} · {day["date"]}</h2><div class="row">{cells}</div><pre>{html.escape(day["caption"])}</pre></section>')
    page = f"""<!doctype html><html><head><meta charset="utf-8"><title>Kingcrab IG preview</title>{GOOGLE_FONTS}<style>{BASE_CSS}
body{{font-family:'Sarabun',sans-serif;background:#ece8e2;margin:0;padding:20px}} section{{background:#fff;border-radius:14px;padding:16px;margin:0 0 18px}}
h2{{font-family:'Kanit';margin:0 0 10px}} .row{{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px}}
.cell{{width:{W * scale}px;height:{H * scale}px;flex:none;border-radius:8px;overflow:hidden}} .sc{{transform:scale({scale});transform-origin:0 0}}
pre{{white-space:pre-wrap;font-family:'Sarabun';background:#faf7f2;padding:10px;border-radius:8px;margin-top:8px}}</style></head>
<body>{''.join(secs)}</body></html>"""
    Path(out_html).write_text(page, encoding="utf-8")
    print("preview written", out_html)


def render(days, out_dir):
    from playwright.sync_api import sync_playwright

    out = Path(out_dir)
    fonts = local_fonts()
    tmp = Path("/tmp/kc_slide.html")
    with sync_playwright() as p:
        exe = "/usr/bin/google-chrome" if Path("/usr/bin/google-chrome").exists() else None
        browser = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H})
        for day in days:
            d = out / day["date"]
            if (d / ".posted").exists():
                print("skip (already posted)", day["date"])
                continue
            d.mkdir(parents=True, exist_ok=True)
            for old in d.glob("*.jpg"):
                old.unlink()
            n = len(day["slides"])
            assert 2 <= n <= 10, f"{day['date']}: carousel needs 2-10 slides"
            for i, s in enumerate(day["slides"]):
                tmp.write_text(slide_doc(s, i, n, fonts), encoding="utf-8")
                page.goto(tmp.as_uri(), wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                page.screenshot(path=str(d / f"{i + 1:02d}.jpg"), type="jpeg", quality=90)
            (d / "caption.txt").write_text(day["caption"], encoding="utf-8")
            print("rendered", day["date"], n, "slides")
        browser.close()


if __name__ == "__main__":
    data = []
    args = sys.argv[1:]
    if "--preview" in args:
        k = args.index("--preview")
        out_html = args[k + 1]
        files = args[:k]
    else:
        out_html, files = None, args[:-1]
    for f in files:
        data += json.loads(Path(f).read_text(encoding="utf-8"))
    if out_html:
        preview(data, out_html)
    else:
        render(data, args[-1])
