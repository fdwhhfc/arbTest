import html
import json
import re
import sys
import urllib.request
import urllib.error

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        data = r.read()
        return r.geturl(), r.headers, data

def text_fetch(url):
    final, headers, data = fetch(url)
    return final, data.decode("utf-8", "ignore")

for image_id in ["167184989", "167246937", "169122059"]:
    try:
        final, s = text_fetch(f"https://pbase.com/image_expo/image/{image_id}")
    except Exception as e:
        print("PBASE_FETCH_ERROR", image_id, repr(e))
        continue
    print("===== PBASE", image_id, "FINAL", final, "LEN", len(s), "=====")
    urls = []
    for m in re.finditer(r'''(?:src|href)\s*=\s*["']([^"']+)["']''', s, re.I):
        u = html.unescape(m.group(1))
        if u.startswith("//"):
            u = "https:" + u
        elif u.startswith("/"):
            u = "https://pbase.com" + u
        if "pbase" in u.lower() or ".jpg" in u.lower() or "original" in u.lower():
            urls.append(u)
    print("PBASE_URLS", json.dumps(list(dict.fromkeys(urls))[:300]))
    for needle in ["original", "Margarida", "exif", "image_id", "167184989"]:
        positions = [m.start() for m in re.finditer(re.escape(needle), s, re.I)]
        for pos in positions[:5]:
            print("AROUND", needle, s[max(0,pos-800):pos+1600].replace("\n"," ")[:2500])

try:
    final, mm = text_fetch("https://www.modelmayhem.com/pussinbootz")
    print("===== MM FINAL", final, "LEN", len(mm), "=====")
    for needle in ["Verified Credits", "Picture by Victor", "See 5 More", "Margarida", "Demonia SG"]:
        positions = [m.start() for m in re.finditer(re.escape(needle), mm, re.I)]
        print("MM_NEEDLE", needle, "COUNT", len(positions))
        for pos in positions[:10]:
            print("MM_AROUND", needle, mm[max(0,pos-8000):pos+12000].replace("\n"," ")[:20000])
    # Collect URLs and data-* attributes near credits area.
    i = mm.lower().find("verified credits")
    chunk = mm[max(0, i-10000):i+120000] if i >= 0 else mm
    links = []
    for m in re.finditer(r'''href=["']([^"']+)["'][^>]*>(.*?)</a>''', chunk, re.I|re.S):
        href = html.unescape(m.group(1))
        label = html.unescape(re.sub(r"<[^>]+>", " ", m.group(2)))
        label = re.sub(r"\s+", " ", label).strip()
        if label or "modelmayhem" in href:
            links.append((label[:160], href[:400]))
    print("MM_LINKS", json.dumps(links[:1000]))
    attrs = re.findall(r'''data-[a-zA-Z0-9_-]+=["'][^"']+["']''', chunk)
    print("MM_DATA_ATTRS", json.dumps(list(dict.fromkeys(attrs))[:1000]))
except Exception as e:
    print("MM_FETCH_ERROR", repr(e))
