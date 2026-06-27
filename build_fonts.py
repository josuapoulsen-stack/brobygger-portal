import urllib.request, re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = r'C:\Users\Josua Poulsen\Documents\Claude Code\brobygger-portal'
HTML = os.path.join(ROOT, 'Brobygger portal.html')
FONTS = os.path.join(ROOT, 'fonts')
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CSS_URL = ("https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800"
           "&family=JetBrains+Mono:wght@400;500;600;700&display=swap")

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if binary else r.read().decode('utf-8')

css = fetch(CSS_URL)
blocks = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*@font-face\s*\{([^}]*)\}", css)
os.makedirs(FONTS, exist_ok=True)
faces, total = [], 0
for subset, body in blocks:
    if subset != "latin":
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    wght = re.search(r"font-weight:\s*(\d+)", body).group(1)
    url = re.search(r"url\(([^)]+)\)", body).group(1)
    slug = fam.lower().replace(' ', '-') + '-' + wght
    fname = slug + '.woff2'
    data = fetch(url, binary=True)
    with open(os.path.join(FONTS, fname), 'wb') as f:
        f.write(data)
    faces.append((fam, wght, fname)); total += len(data)
    print(f"  hentet  fonts/{fname}  ({len(data)//1024} KB)")

# Byg @font-face CSS (latin, ingen unicode-range → bruges til al tekst)
face_css = "\n".join(
    f"    @font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url('fonts/{fn}') format('woff2');}}"
    for fam, w, fn in faces
)
style_block = "  <!-- Self-hostede fonts (ingen Google CDN — GDPR) -->\n  <style>\n" + face_css + "\n  </style>"

with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

old_links = """  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link href="https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>"""

ok = []
if old_links in html:
    html = html.replace(old_links, style_block, 1); ok.append("links→@font-face")
else:
    print("FAIL: font-links ikke fundet");

# Stram CSP: fjern Google-domæner
csp_old_style = "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com"
csp_old_font  = "font-src 'self' data: https://fonts.gstatic.com"
if csp_old_style in html:
    html = html.replace(csp_old_style, "style-src 'self' 'unsafe-inline'", 1); ok.append("CSP style-src")
if csp_old_font in html:
    html = html.replace(csp_old_font, "font-src 'self'", 1); ok.append("CSP font-src")

with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\nFiler: {len(faces)}  ·  i alt {total//1024} KB")
print("Patches:", ", ".join(ok))
