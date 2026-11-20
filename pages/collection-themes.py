"""Add the SPK collection to the existing assets without replacing legacy palettes."""
import json
import sys
from pathlib import Path

ROWS = [
 [
  "Aurora",
  "Северное сияние",
  "Изумруд, бирюза и холодный фиолетовый",
  "dark",
  "10292a",
  "183a39",
  "77f4be",
  "ad91fa",
  "ecfff7",
  "a4d3c4",
  "dff4e9",
  "eefbf5",
  "087c66",
  "9674c7",
  "163a32",
  "457368",
  0.3,
  0.45,
  145,
  24
 ],
 [
  "Midnight",
  "Синяя полночь",
  "Кобальт и серебристый индиго",
  "dark",
  "090e29",
  "1a2251",
  "9eb4ff",
  "6f78ff",
  "f1f3ff",
  "aeb9e5",
  "e3e9ff",
  "f1f4ff",
  "394eb6",
  "8c80e6",
  "27325d",
  "53648b",
  0.22,
  0.35,
  155,
  28
 ],
 [
  "Cyberpunk",
  "Голограмма",
  "Малиновый неон и электрическая бирюза",
  "dark",
  "1d0828",
  "3d1248",
  "ff8bea",
  "47f2df",
  "fff1ff",
  "ddacd9",
  "fce7ff",
  "fff0fc",
  "a02391",
  "159e9a",
  "4c2053",
  "80527f",
  0.36,
  0.46,
  115,
  14
 ],
 [
  "AMOLED",
  "Абсолютный чёрный",
  "Чистый чёрный фон и белые акценты",
  "dark",
  "000000",
  "101010",
  "f4f4f4",
  "747474",
  "ffffff",
  "b0b0b0",
  "ffffff",
  "f6f6f6",
  "131313",
  "6e6e6e",
  "161616",
  "606060",
  0.025,
  0.045,
  90,
  36
 ],
 [
  "Forest",
  "Изумрудный лес",
  "Хвойный зелёный и оттенок золота",
  "dark",
  "0d261b",
  "153e29",
  "8be4a0",
  "d8b76b",
  "edfff2",
  "a9d0b6",
  "e0f0dd",
  "f1f8e9",
  "276539",
  "b38a37",
  "213b2c",
  "526e4f",
  0.24,
  0.28,
  165,
  25
 ],
 [
  "Crimson",
  "Багровый бархат",
  "Винный красный и глубокий бордовый",
  "dark",
  "210810",
  "491321",
  "ff8b9e",
  "a82c54",
  "fff0f3",
  "e0aeb9",
  "f8dce2",
  "fff0f2",
  "a51e42",
  "cf748e",
  "5b182b",
  "855465",
  0.25,
  0.37,
  135,
  26
 ],
 [
  "Ocean",
  "Морская бездна",
  "Насыщенный синий и свет морской волны",
  "dark",
  "061d31",
  "103856",
  "70e4f5",
  "2872e3",
  "eefaff",
  "9dc7df",
  "d9effb",
  "ebf9ff",
  "176ca4",
  "36b4cc",
  "1e3b55",
  "4b708a",
  0.29,
  0.43,
  170,
  21
 ],
 [
  "Amber",
  "Медный янтарь",
  "Тёмная медь, бронза и огненный оранжевый",
  "dark",
  "29170b",
  "432818",
  "ffbd74",
  "c76b36",
  "fff1da",
  "e5ba99",
  "f8e4ce",
  "fff2df",
  "95501b",
  "c78042",
  "553325",
  "806044",
  0.28,
  0.4,
  122,
  23
 ],
 [
  "Graphite",
  "Титан",
  "Холодный металл и точечные янтарные акценты",
  "dark",
  "1b222b",
  "313b48",
  "bfcedd",
  "e5b761",
  "f3f7fc",
  "b1bfce",
  "e5e9ee",
  "f3f6fa",
  "485969",
  "be832d",
  "273342",
  "5e6e7f",
  0.11,
  0.16,
  110,
  30
 ],
 [
  "Sakura",
  "Цветущая сакура",
  "Розовый фарфор и цвет вишнёвых лепестков",
  "light",
  "fce1eb",
  "fff1f6",
  "b13469",
  "e29abe",
  "51243c",
  "88546e",
  "2b1120",
  "452238",
  "ff9ec7",
  "d15d9d",
  "fff0f7",
  "e0abc6",
  0.27,
  0.4,
  140,
  23
 ],
 [
  "Lavender",
  "Лавандовый туман",
  "Мягкий сиреневый и тёплый жемчужный свет",
  "light",
  "e8dcf9",
  "f8f1ff",
  "73509a",
  "c2a6df",
  "402a56",
  "6f5a83",
  "21152e",
  "332246",
  "cfadff",
  "9b70d1",
  "f5ecff",
  "c7afd8",
  0.19,
  0.34,
  155,
  28
 ],
 [
  "Mint",
  "Мятное стекло",
  "Прозрачная мята, аквамарин и белый",
  "light",
  "d9f7f4",
  "effffc",
  "087d72",
  "73dbce",
  "194e49",
  "477973",
  "092a29",
  "16423e",
  "77f0d7",
  "4fbcc7",
  "eafff9",
  "9ad5ce",
  0.22,
  0.38,
  105,
  22
 ],
 [
  "Cream",
  "Ванильный крем",
  "Тёплый бежевый и карамельный кофе",
  "light",
  "efe1ca",
  "fff6e5",
  "88552e",
  "c59d72",
  "4b3324",
  "806c58",
  "241b12",
  "3a2b1e",
  "e2bc91",
  "b08b62",
  "fff4e5",
  "c5b29a",
  0.08,
  0.18,
  90,
  32
 ],
 [
  "Glacier",
  "Ледник",
  "Снег, ледяной голубой и стальной синий",
  "light",
  "dcedf8",
  "f4fbff",
  "206a91",
  "9fcedd",
  "263e52",
  "527589",
  "16232e",
  "283d4e",
  "b0d8ec",
  "7199bb",
  "f0faff",
  "b4c9d8",
  0.14,
  0.25,
  160,
  29
 ],
 [
  "Peach",
  "Персиковый рассвет",
  "Абрикосовый свет и коралловый акцент",
  "light",
  "ffe3cf",
  "fff2e6",
  "b74d2c",
  "ed9c70",
  "603623",
  "925c46",
  "321a12",
  "542d20",
  "ffb09a",
  "e8754e",
  "fff0e5",
  "efb3a0",
  0.32,
  0.42,
  125,
  20
 ],
 [
  "Paper",
  "Бумага и чернила",
  "Молочная бумага, чёрнильный синий и строгие линии",
  "light",
  "f1efe7",
  "fffdf6",
  "26354b",
  "9ea9b4",
  "202b3b",
  "626e7b",
  "1b1e24",
  "282e38",
  "d8dce0",
  "8795a7",
  "f5f4ed",
  "b8bfc8",
  0.025,
  0.05,
  90,
  36
 ],
 [
  "Matcha",
  "Зелёный чай",
  "Оливковый зелёный и листья чая",
  "light",
  "e3e7c4",
  "f4f6dd",
  "576b24",
  "acbf54",
  "394224",
  "69774b",
  "222810",
  "373e1c",
  "d3e67e",
  "a7b749",
  "f7f9e8",
  "bfc9a2",
  0.19,
  0.3,
  145,
  27
 ],
 [
  "Summer",
  "Солнечный день",
  "Сочный жёлтый и яркий небесно-синий",
  "light",
  "fff1a8",
  "fff9d7",
  "805600",
  "e5b924",
  "504017",
  "806d35",
  "2e2609",
  "4c3c13",
  "ffe171",
  "8aceef",
  "fff8e2",
  "dbca9c",
  0.33,
  0.46,
  115,
  18
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
    slug,name,desc,preferred,*values=row
    colors=values[:12]
    intensity_a,intensity_b,angle,speed=values[12:]
    id="collection-"+slug.lower()
    other="dark" if preferred=="light" else "light"
    modes={preferred:dict(zip(keys,("#"+v for v in colors[:6]))),other:dict(zip(keys,("#"+v for v in colors[6:])) )}
    base[id]=modes
    metadata.append(dict(id=id,name=name,description=desc,category="collection"))
    for mode,c in modes.items():
        bg,panel,accent,secondary,text,muted=(c[k] for k in keys)
        text=readable(text,[bg,panel],ink(bg))
        panel2=tint(panel,text,.075,text)
        start=tint(panel,accent,intensity_a,text)
        end=tint(panel,secondary,intensity_b,text)
        mid=panel
        surfaces=[bg,panel,panel2,start,end]
        muted=readable(muted,surfaces,text)
        green=readable(accent,surfaces,text)
        on=ink(accent)
        button_end=tint(accent,secondary,min(.62,intensity_b*1.2),on)
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
        values["collectionAngle"]=str(angle)+"deg"
        values["collectionSpeed"]=str(speed)+"s"
        css.append(selectors+"{"+ ";".join("--"+k+":"+v for k,v in values.items())+";}")

# Explicit dark declarations must follow light declarations regardless of preferred variant.
css.sort(key=lambda s: '[data-theme="dark"]' in s)
def catalog(s):
    s=replace_once(s,'"id": "dot-lime", "name": "Лайм"','"id": "dot-lime", "name": "Лайм · контраст"')
    s=replace_once(s,'"id": "dot-amber", "name": "Янтарь"','"id": "dot-amber", "name": "Янтарь · контраст"')
    s=replace_once(s,"name:'Неон-сити'","name:'Неоновые улицы'")
    return replace_once(s,"\n]);",",\n"+",\n".join(json.dumps(m,ensure_ascii=False) for m in metadata)+"\n]);")
patch("palettes.js",catalog)
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
:root[data-palette^="collection-"]:not([data-custom-design="on"]) :is(.hero,.lesson,.now-next){background:linear-gradient(var(--collectionAngle,125deg),var(--panelStart),var(--panelMid) 48%,var(--panelEnd))}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) .button-primary{background:linear-gradient(120deg,var(--buttonStart),var(--buttonMid),var(--buttonEnd));color:var(--onButton)}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) :is(.days>.selection-glider,.week-tabs>.selection-glider,.sub-tabs>.selection-glider,.campus-glider,.nav-item.active>span:first-child){background:linear-gradient(120deg,var(--limeStart),var(--limeMid),var(--limeEnd))}
:root[data-palette^="collection-"]:not([data-custom-design="on"]) [data-slider-ready]>.active{color:var(--onLime)}
:root[data-palette^="collection-"]:not([data-custom-design="on"])[data-motion="on"] :is(.hero,.lesson,.now-next){background-size:170% 170%;animation:collection-flow var(--collectionSpeed,19s) ease-in-out infinite alternate}
:root[data-motion="on"] :is(.lesson,.hero,.settings-card,.fav-card,.spk-room-grid span,.palette-choice){transition:background-color 320ms ease,color 320ms ease,border-color 320ms ease}
.palette-sample[data-palette^="collection-"] .sample-hero{background:linear-gradient(var(--collectionAngle,120deg),var(--heroStart),var(--heroMid),var(--heroEnd))}
.palette-sample[data-palette^="collection-"] .sample-bottom>i,.palette-sample[data-palette^="collection-"] .sample-hero i:last-child{background:linear-gradient(120deg,var(--limeStart),var(--limeMid),var(--limeEnd))}
.palette-sample[data-palette^="collection-"] .sample-bottom>span{background:linear-gradient(var(--collectionAngle,120deg),var(--panelStart),var(--panelEnd))}
@keyframes collection-flow{from{background-position:0% 30%}to{background-position:100% 70%}}
"""
patch("web.css",lambda s:s+"\n/* SPK Collection */\n"+"\n".join(css)+"\n"+styles)
assert len(base)==18
assert len({p["name"] for p in metadata})==18
assert all(not any("A"<=c<="Z" or "a"<=c<="z" for c in p["name"]) for p in metadata)
print("18 collection palettes / 36 mode variants; contrast checks passed")
