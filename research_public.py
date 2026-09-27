import html, re, urllib.request, json

url="https://www.modelmayhem.com/pussinbootz"
req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/137 Safari/537.36"})
s=urllib.request.urlopen(req,timeout=45).read().decode("utf-8","ignore")

# isolate verified credits area through Tags heading
a=s.lower().find("verified credits")
b=s.lower().find("id='tags-container'", a)
if b < 0:
    b=s.lower().find('id="tags-container"', a)
chunk=s[a:b if b>0 else len(s)]

blocks=re.split(r"<div class=['\"]single-credit-container['\"]>",chunk,re.I)[1:]
rows=[]
for block in blocks:
    name=""
    m=re.search(r"<div class=['\"]credit-username['\"]>\s*(.*?)</div>",block,re.I|re.S)
    if m:
        name=html.unescape(re.sub(r"<[^>]+>"," ",m.group(1)))
        name=re.sub(r"\s+"," ",name).strip()
    href=""
    m=re.search(r"<a class=['\"]clickable-credit['\"] href=['\"]([^'\"]+)['\"]",block,re.I)
    if m: href=html.unescape(m.group(1))
    recent=""
    m=re.search(r"Worked together\s*(.*?)</span>",block,re.I|re.S)
    if m:
        recent=html.unescape(re.sub(r"<[^>]+>"," ",m.group(1)))
        recent=re.sub(r"\s+"," ",recent).strip()
    praise=""
    m=re.search(r"<p class=['\"]praise-container['\"]>(.*?)</p>",block,re.I|re.S)
    if m:
        praise=html.unescape(re.sub(r"<[^>]+>"," ",m.group(1)))
        praise=re.sub(r"\s+"," ",praise).replace("Read less","").strip()
    samples=[]
    for mm in re.finditer(r"<input class=['\"]image_samples['\"][^>]*>",block,re.I):
        tag=mm.group(0)
        attrs=dict((k.lower(),html.unescape(v)) for k,v in re.findall(r"([a-zA-Z0-9_-]+)=['\"]([^'\"]*)['\"]",tag))
        samples.append({
            "pic_url":attrs.get("pic_url",""),
            "value":attrs.get("value",""),
            "owner_name":attrs.get("owner_name","")
        })
    if name or href or recent:
        rows.append({"name":name,"href":href,"recent":recent,"praise":praise,"samples":samples})

print("VERIFIED_CREDITS_JSON="+json.dumps(rows,ensure_ascii=False))
print("CREDIT_COUNT="+str(len(rows)))

# Search entire source for photographer/profile indicators that resemble Jean-Francois/image-expo.
for needle in ["Jean-Francois","Jean Francois","image-expo","image_expo","imageexpo"]:
    pos=[m.start() for m in re.finditer(re.escape(needle),s,re.I)]
    print("NEEDLE",needle,"COUNT",len(pos))
    for p in pos[:20]:
        x=re.sub(r"\s+"," ",s[max(0,p-800):p+1200])
        print("CTX",needle,x)

# Output all profile href/name pairs around verified credits for independent inspection.
pairs=[]
for m in re.finditer(r"<a class=['\"]clickable-credit['\"] href=['\"]([^'\"]+)['\"]>(.*?)</a>",chunk,re.I|re.S):
    href=html.unescape(m.group(1))
    text=html.unescape(re.sub(r"<[^>]+>"," ",m.group(2)))
    text=re.sub(r"\s+"," ",text).strip()
    pairs.append((href,text[:300]))
print("CREDIT_LINKS="+json.dumps(pairs,ensure_ascii=False))
