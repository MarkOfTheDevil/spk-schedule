"""Add the SPK collection to the existing assets without replacing legacy palettes."""
import json
import sys
from pathlib import Path

ROWS = [
 [
  "Aurora",
  "Северное сияние",
  "dark",
  "101b24",
  "1c303b",
  "79e9bb",
  "64b8e7",
  "ecfff8",
  "a1bdc5",
  "e8f6f2",
  "fbfffd",
  "27765d",
  "90cde9",
  "203e37",
  "567469"
 ],
 [
  "Midnight",
  "Полночь",
  "dark",
  "101224",
  "20243d",
  "b1b7ff",
  "777af9",
  "f0efff",
  "a8abc8",
  "eeeffd",
  "ffffff",
  "5148aa",
  "b0b7f8",
  "302c58",
  "746e91"
 ],
 [
  "Cyberpunk",
  "Неоновый город",
  "dark",
  "171020",
  "30203d",
  "f485ed",
  "6deee3",
  "fff0ff",
  "c4a8cd",
  "fff0fb",
  "ffffff",
  "a32b98",
  "64cfc9",
  "492447",
  "81577d"
 ],
 [
  "AMOLED",
  "Абсолютный чёрный",
  "dark",
  "000000",
  "171717",
  "f2f2f2",
  "777777",
  "ffffff",
  "aaaaaa",
  "f4f4f4",
  "ffffff",
  "252525",
  "aaaaaa",
  "161616",
  "646464"
 ],
 [
  "Forest",
  "Хвойный лес",
  "dark",
  "122019",
  "21392b",
  "ade0a5",
  "70b68a",
  "edf8ed",
  "a6bcac",
  "edf5ea",
  "fcfffb",
  "3e7041",
  "a5c9a3",
  "293f2d",
  "607660"
 ],
 [
  "Crimson",
  "Бордовый бархат",
  "dark",
  "211118",
  "38202a",
  "ff9cae",
  "b94b69",
  "ffeef2",
  "c9a5b0",
  "fbe9ed",
  "fffafb",
  "a13755",
  "e9a5b8",
  "502b36",
  "885d6a"
 ],
 [
  "Ocean",
  "Глубины океана",
  "dark",
  "0b2031",
  "15394c",
  "71d9f2",
  "4198d1",
  "edfaff",
  "9fc5d7",
  "e7f4fa",
  "ffffff",
  "276b96",
  "9bd7ed",
  "243d50",
  "607e91"
 ],
 [
  "Amber",
  "Тёплый янтарь",
  "dark",
  "211a13",
  "382b1d",
  "ffd08a",
  "c78b48",
  "fff4df",
  "c4b39b",
  "fff3dd",
  "fffdfa",
  "8b561b",
  "ebbc79",
  "4e3823",
  "826e52"
 ],
 [
  "Graphite",
  "Металл и графит",
  "dark",
  "1a1d21",
  "2b3036",
  "b5ccd9",
  "829aa8",
  "f2f5f8",
  "adb5be",
  "eff2f5",
  "ffffff",
  "48616f",
  "bbcbd5",
  "273239",
  "66747e"
 ],
 [
  "Sakura",
  "Цветение сакуры",
  "light",
  "fff2f5",
  "ffffff",
  "a83f69",
  "f3b7cc",
  "472332",
  "8a6475",
  "24131b",
  "39232f",
  "ffb0d0",
  "d77aa0",
  "fff1f7",
  "cba5b6"
 ],
 [
  "Lavender",
  "Лавандовый туман",
  "light",
  "efedfa",
  "ffffff",
  "6951b1",
  "c9baee",
  "342957",
  "766c90",
  "181426",
  "2a2342",
  "c8b5ff",
  "9b83e2",
  "f4eeff",
  "bcb1d4"
 ],
 [
  "Mint",
  "Мятная свежесть",
  "light",
  "e7f5ef",
  "fafffc",
  "27765d",
  "a6dcc5",
  "20483b",
  "57776a",
  "0e211a",
  "20392e",
  "a2e7cc",
  "62b898",
  "edfff7",
  "a6bfb2"
 ],
 [
  "Cream",
  "Тёплый минимализм",
  "light",
  "f3ede2",
  "fffaf1",
  "926234",
  "d8bd91",
  "48392a",
  "82725f",
  "211a13",
  "352b20",
  "e7c197",
  "b89a70",
  "fff4e5",
  "c7b69e"
 ],
 [
  "Glacier",
  "Ледяной голубой",
  "light",
  "e9f3fb",
  "ffffff",
  "306c9e",
  "add9f5",
  "253d55",
  "627b90",
  "101e2d",
  "22364b",
  "a4d7ff",
  "6ea8d5",
  "eff8ff",
  "a9bed2"
 ],
 [
  "Peach",
  "Персиковый рассвет",
  "light",
  "fff0e5",
  "fffaf6",
  "b65035",
  "ffc29e",
  "573326",
  "936b59",
  "291810",
  "41291f",
  "ffc0a0",
  "d88664",
  "fff0e6",
  "d1ad99"
 ],
 [
  "Paper",
  "Чистая типографика",
  "light",
  "f4f4f2",
  "ffffff",
  "303030",
  "b6b6b2",
  "202020",
  "6e6e69",
  "191919",
  "292929",
  "eeeeeb",
  "969692",
  "f5f5f2",
  "b9b9b3"
 ],
 [
  "Matcha",
  "Японский минимализм",
  "light",
  "edf0df",
  "f9fbf3",
  "597334",
  "b7cb91",
  "35412b",
  "6b795e",
  "192116",
  "293524",
  "c5df8f",
  "8aa961",
  "f5f9e9",
  "b6c5a6"
 ],
 [
  "Summer",
  "Летнее солнце",
  "light",
  "fff6cf",
  "fffdf5",
  "85620f",
  "f4cc60",
  "4e421d",
  "7e7148",
  "242013",
  "39301b",
  "ffe18a",
  "c6a94f",
  "fff8df",
  "cabd94"
 ]
]
root = Path(sys.argv[1])
def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one anchor: {old[:100]}")
    return text.replace(old, new, 1)

def patch(name, fn):
    p = root / name
    p.write_text(fn(p.read_text(encoding="utf-8")), encoding="utf-8")

def rgb(c):
    return tuple(int(c[i:i+2], 16) for i in (1,3,5))

def mix(a,b,t):
    return "#" + "".join(f"{round(x+(y-x)*t):02x}" for x,y in zip(rgb(a),rgb(b)))

def lum(c):
    values = [v/255 for v in rgb(c)]
    return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip((.2126,.7152,.0722),values))

def ratio(a,b):
    a,b = sorted((lum(a),lum(b)))
    return (b+.05)/(a+.05)

def ink(c):
    return "#000000" if ratio("#000000",c)>=ratio("#ffffff",c) else "#ffffff"

def readable(c, backgrounds, fallback):
    for i in range(101):
        candidate=mix(c,fallback,i/100)
        if all(ratio(candidate,b)>=4.5 for b in backgrounds):
            return candidate
    raise ValueError("No accessible color for given backgrounds")

def tint(bg,c,amount,fg):
    for i in range(round(amount*100),-1,-1):
        v=mix(bg,c,i/100)
        if ratio(v,fg)>=4.5:
            return v
    raise ValueError("Invalid foreground")

keys=("background","panel","accent","secondary","text","muted")
base={}
metadata=[]
css=[]
for row in ROWS:
    name,desc,preferred,*colors=row
    id="collection-"+name.lower()
    other="dark" if preferred=="light" else "light"
    modes={preferred:dict(zip(keys,("#"+v for v in colors[:6]))),other:dict(zip(keys,("#"+v for v in colors[6:])) )}
    base[id]=modes
    metadata.append(dict(id=id,name=name,description=desc,category="collection"))
    for mode,c in modes.items():
        bg,panel,accent,secondary,text,muted=(c[k] for k in keys)
        text=readable(text,[bg,panel],ink(bg))
        panel2=tint(panel,text,.075,text)
        start=tint(panel,accent,.13,text)
        end=tint(panel,secondary,.18,text)
        mid=panel
        surfaces=[bg,panel,panel2,start,end]
        muted=readable(muted,surfaces,text)
        green=readable(accent,surfaces,text)
        on=ink(accent)
        button_end=tint(accent,secondary,.28,on)
        button_mid=mix(accent,button_end,.5)
        button_end=tint(accent,button_end,1,on)
        accent_bg=tint(panel,accent,.16,text)
        values=dict(bg=bg,panel=panel,panel2=panel2,text=text,muted=muted,line=mix(panel,text,.23),green=green,accent=accent_bg,accentText=text,hero=panel,heroText=text,heroMuted=muted,lime=accent,onLime=on,onButton=on,heroStart=start,heroMid=mid,heroEnd=end,panelStart=start,panelMid=mid,panelEnd=end,buttonStart=accent,buttonMid=button_mid,buttonEnd=button_end,limeStart=accent,limeMid=button_mid,limeEnd=button_end,accentStart=accent_bg,accentMid=panel2,accentEnd=accent_bg,glow=accent+"22",glowSoft=accent+"13")
        assert all(ratio(values["text"],v)>=4.5 for v in surfaces)
        assert all(ratio(values["onLime"],v)>=4.5 for v in (accent,button_mid,button_end))
        assert all(ratio(values["muted"],v)>=4.5 and ratio(values["green"],v)>=4.5 for v in surfaces)
        prefix=':root' if mode=="light" else ':root[data-theme="dark"]'
        selectors=f'{prefix}[data-palette="{id}"],{prefix} .palette-sample[data-palette="{id}"]'
        if mode=="light":
            selectors=f':root[data-palette="{id}"],.palette-sample[data-palette="{id}"]'
        css.append(selectors+"{"+ ";".join("--"+k+":"+v for k,v in values.items())+";}")

# Explicit dark declarations must follow light declarations regardless of preferred variant.
css.sort(key=lambda s: '[data-theme="dark"]' in s)
patch("palettes.js",lambda s:replace_once(s,"\n]);",",\n"+",\n".join(json.dumps(m,ensure_ascii=False) for m in metadata)+"\n]);"))
def appearance(s):
    s=replace_once(s," const defaults=", " Object.assign(BASE,"+json.dumps(base,ensure_ascii=False,separators=(",",":"))+");\n const defaults=")
    old="return {...base,panel:mix(base.background,'#ffffff',luminance(base.background)<.179?.065:.7),text:ink(base.background),muted:mix(ink(base.background),base.background,.3),...config.colors[mode]};"
    new="const preset=config.base.startsWith('collection-')&&!config.colors[mode].background;return {...base,panel:preset?base.panel:mix(base.background,'#ffffff',luminance(base.background)<.179?.065:.7),text:preset?base.text:ink(base.background),muted:preset?base.muted:mix(ink(base.background),base.background,.3),...config.colors[mode]};"
    return replace_once(s,old,new)
patch("appearance.js",appearance)
for page in ("index.html","404.html"):
    def html(s):
        s=replace_once(s,'>Все · 30</button>','>Все · 48</button>')
        s=replace_once(s,'>Неон · 8</button>','>Неон · 8</button>\n        <button class="chip" data-palette-filter="collection" aria-pressed="false">Коллекция · 18</button>')
        return s
    patch(page,html)
patch("app.js",lambda s:replace_once(s,"state.paletteFilter=currentPalette().category==='neon'?'neon':'all';","state.paletteFilter=['neon','collection'].includes(currentPalette().category)?currentPalette().category:'all';"))
# App styles come last; preserve custom design and the existing motion/reduced-motion settings.
styles="""
:root[data-palette^="collection-"]:not([data-custom-design="on"]) :is(.hero,.lesson,.now-next){background:linear-gradient(125deg,var(--panelStart),var(--panelMid) 48%,var(--panelEnd))}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) .button-primary{background:linear-gradient(120deg,var(--buttonStart),var(--buttonMid),var(--buttonEnd));color:var(--onButton)}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) :is(.days>.selection-glider,.week-tabs>.selection-glider,.sub-tabs>.selection-glider,.campus-glider,.nav-item.active>span:first-child){background:linear-gradient(120deg,var(--limeStart),var(--limeMid),var(--limeEnd))}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) [data-slider-ready]>.active{color:var(--onLime)}
:root[data-palette^="collection-"]:not([data-custom-design="on"])[data-motion="on"] :is(.hero,.lesson,.now-next){background-size:170% 170%;animation:collection-flow 19s ease-in-out infinite alternate}
:root[data-motion="on"] :is(.lesson,.hero,.settings-card,.fav-card,.spk-room-grid span,.palette-choice){transition:background-color 320ms ease,color 320ms ease,border-color 320ms ease}
.palette-sample[data-palette^="collection-"] .sample-hero{background:linear-gradient(120deg,var(--heroStart),var(--heroMid),var(--heroEnd))}
.palette-sample[data-palette^="collection-"] .sample-bottom>i,.palette-sample[data-palette^="collection-"] .sample-hero i:last-child{background:linear-gradient(120deg,var(--limeStart),var(--limeMid),var(--limeEnd))}
.palette-sample[data-palette^="collection-"] .sample-bottom>span{background:linear-gradient(120deg,var(--panelStart),var(--panelEnd))}
@keyframes collection-flow{from{background-position:0% 30%}to{background-position:100% 70%}}
"""
patch("web.css",lambda s:s+"\n/* SPK Collection */\n"+"\n".join(css)+"\n"+styles)
assert len(base)==18
print("18 collection palettes / 36 mode variants; contrast checks passed")
