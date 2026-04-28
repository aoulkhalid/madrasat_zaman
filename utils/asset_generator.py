"""
utils/asset_generator.py
Génère toutes les images (logos, différences) et sons (WAV) manquants
"""
import os, math, wave, struct, random
from PIL import Image, ImageDraw

from config import LOGOS_DIR, DIFF_DIR, SOUNDS_DIR
from games.logo_data import ALL_LOGOS

# ═══════════════════════════════════════════════════════════════════════════════
# LOGOS — 60 logos stylisés générés par PIL
# ═══════════════════════════════════════════════════════════════════════════════

LOGO_THEMES = [
    # (bg_start, bg_end, shape, text_color)
    ((20,80,160),  (40,120,200), "circle",   (255,255,255)),
    ((20,140,100), (40,180,130), "hexagon",  (255,255,255)),
    ((200,80,0),   (230,120,20), "star",     (255,255,255)),
    ((100,20,150), (140,50,190), "diamond",  (255,255,255)),
    ((180,20,60),  (210,50,90),  "circle",   (255,255,255)),
    ((0,100,100),  (20,140,140), "hexagon",  (255,255,255)),
    ((30,50,130),  (60,90,170),  "circle",   (255,255,255)),
    ((140,80,0),   (180,120,30), "star",     (255,255,255)),
    ((0,120,80),   (30,160,110), "diamond",  (255,255,255)),
    ((120,0,60),   (160,30,90),  "circle",   (255,255,255)),
]

def _gradient_bg(img, c1, c2):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    for y in range(h):
        r = int(c1[0] + (c2[0]-c1[0]) * y/h)
        g = int(c1[1] + (c2[1]-c1[1]) * y/h)
        b = int(c1[2] + (c2[2]-c1[2]) * y/h)
        draw.rectangle([(0,y),(w,y+1)], fill=(r,g,b))

def _draw_shape(draw, cx, cy, r, shape, color):
    if shape == "circle":
        draw.ellipse([(cx-r,cy-r),(cx+r,cy+r)], fill=color, outline=(255,255,255,80), width=2)
    elif shape == "hexagon":
        pts = [(cx + r*math.cos(math.radians(a*60-90)),
                cy + r*math.sin(math.radians(a*60-90))) for a in range(6)]
        draw.polygon(pts, fill=color)
    elif shape == "star":
        pts = []
        for a in range(10):
            rad = r if a%2==0 else r//2
            angle = math.radians(a*36 - 90)
            pts.append((cx + rad*math.cos(angle), cy + rad*math.sin(angle)))
        draw.polygon(pts, fill=color)
    elif shape == "diamond":
        pts = [(cx, cy-r), (cx+r*0.7, cy), (cx, cy+r), (cx-r*0.7, cy)]
        draw.polygon(pts, fill=color)

def _text_centered(draw, text, cy, size, fill, img_w=300):
    try:
        from PIL import ImageFont
        for path in [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]:
            if os.path.exists(path):
                font = ImageFont.truetype(path, size)
                bbox = draw.textbbox((0,0), text, font=font)
                x = (img_w - (bbox[2]-bbox[0])) // 2
                draw.text((x, cy - size//2), text, font=font, fill=fill)
                return
    except: pass
    draw.text((img_w//2 - len(text)*4, cy - size//2), text, fill=fill)

def make_logo(idx: int, name: str) -> Image.Image:
    theme = LOGO_THEMES[idx % len(LOGO_THEMES)]
    c1, c2, shape, txt_c = theme
    img  = Image.new("RGB", (300, 200))
    _gradient_bg(img, c1, c2)
    draw = ImageDraw.Draw(img)
    # Forme principale
    _draw_shape(draw, 150, 85, 52, shape, (255,255,255,50))
    _draw_shape(draw, 150, 85, 38, shape,
                (255,255,255) if shape != "circle" else tuple(min(c+30,255) for c in c1))
    # Initiale(s)
    initials = name[:2] if len(name)>=2 else name[0]
    _text_centered(draw, initials, 90, 28, tuple(c1), 300)
    _text_centered(draw, name, 165, 18, (255,255,255), 300)
    return img

# ═══════════════════════════════════════════════════════════════════════════════
# IMAGES DIFFÉRENCE (3 variantes paramétrées)
# ═══════════════════════════════════════════════════════════════════════════════

def _sky_gradient(draw, w, h, top=(135,206,235), bot=(180,220,240)):
    limit = int(h*0.55)
    for y in range(limit):
        r = int(top[0]+(bot[0]-top[0])*y/limit)
        g = int(top[1]+(bot[1]-top[1])*y/limit)
        b = int(top[2]+(bot[2]-top[2])*y/limit)
        draw.rectangle([(0,y),(w,y+1)], fill=(r,g,b))

def _make_scene(variant=0, is_right=False):
    """3 variantes de scènes avec 5 différences chacune."""
    W, H = 310, 210

    palettes = [
        # sky_top, sky_bot, mtn, grass, lake
        ((135,206,235),(180,220,240),(65,80,100),(60,150,60),(80,140,200)),
        ((180,160,220),(210,190,230),(80,60,90),(40,120,80),(60,100,180)),
        ((220,200,160),(235,220,190),(90,70,50),(80,140,40),(100,160,200)),
    ]
    p = palettes[variant % len(palettes)]

    img  = Image.new("RGB", (W, H), p[0])
    draw = ImageDraw.Draw(img)
    _sky_gradient(draw, W, H, p[0], p[1])

    # Montagnes — diff #2: couleur sommet modifiée sur l'image de droite
    peak_col = (110,70,90) if is_right else p[2]
    draw.polygon([(0,H//2),(W//4,int(H*0.18)),(W//2,H//2)], fill=p[2])
    draw.polygon([(W//4,H//2),(W//2,int(H*0.13)),(3*W//4,H//2)], fill=peak_col)
    draw.polygon([(W//2,H//2),(3*W//4,int(H*0.22)),(W,H//2)], fill=p[2])
    # Neiges
    for cx,cy,r in [(W//2,int(H*0.13),14),(W//4,int(H*0.18),10)]:
        draw.polygon([(cx,cy),(cx-r,cy+r*1.2),(cx+r,cy+r*1.2)],fill=(230,240,255))

    # Sol — diff #5: teinte herbe différente
    grass = (40,120,50) if is_right else p[3]
    draw.rectangle([(0,int(H*0.50)),(W,H)], fill=grass)

    # Lac — diff #3: reflet absent à droite
    lt = int(H*0.60)
    draw.ellipse([(int(W*0.20),lt),(int(W*0.80),H-20)], fill=p[4])
    if not is_right:
        draw.ellipse([(int(W*0.30),lt+15),(int(W*0.70),lt+48)], fill=tuple(min(c+20,255) for c in p[4]))

    # Arbres — diff #4: arbre supprimé à droite
    tree_xs = list(range(15,70,22)) + list(range(270,W,22))
    if not is_right:
        tree_xs.append(int(W*0.88))
    tc = (30,110,30)
    for tx in tree_xs:
        ty = int(H*0.60)
        draw.rectangle([(tx-3,ty-18),(tx+3,ty)], fill=(100,65,35))
        draw.polygon([(tx,ty-55),(tx-18,ty-18),(tx+18,ty-18)], fill=tc)
        draw.polygon([(tx,ty-70),(tx-13,ty-42),(tx+13,ty-42)], fill=(40,130,40))

    # Nuages — diff #1: nuage supprimé à droite
    def cloud(cx,cy):
        draw.ellipse([(cx-30,cy-14),(cx+30,cy+14)],fill=(255,255,255))
        draw.ellipse([(cx-14,cy-22),(cx+14,cy+8)], fill=(255,255,255))
        draw.ellipse([(cx+10,cy-18),(cx+44,cy+10)],fill=(255,255,255))
    cloud(100, 30)
    cloud(230, 45)
    if not is_right:
        cloud(295, 25)

    return img

# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO WAV
# ═══════════════════════════════════════════════════════════════════════════════

def _write_wav(path, samples, rate=44100):
    with wave.open(path, "w") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        f.writeframes(b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s)))) for s in samples))

def _make_calm(path, dur=12):
    rate = 44100
    freqs = [261.63, 329.63, 392.00]
    s = []
    for i in range(rate*dur):
        t = i/rate
        amp = 0.22*(0.5+0.5*math.sin(2*math.pi*0.25*t))
        s.append(sum(math.sin(2*math.pi*f*t) for f in freqs)*amp*32767/3)
    _write_wav(path, s)

def _make_tension(path, dur=12):
    rate = 44100
    freqs = [440.0, 466.16, 523.25]
    s = []
    for i in range(rate*dur):
        t = i/rate
        beat = 0.55+0.45*abs(math.sin(2*math.pi*2.5*t))
        s.append(sum(math.sin(2*math.pi*f*t) for f in freqs)*0.28*beat*32767/3)
    _write_wav(path, s)

def _make_victory(path, dur=8):
    rate = 44100
    notes = [261.63,329.63,392.0,523.25,659.25,783.99]
    s = []
    step = dur*rate//len(notes)
    for ni, freq in enumerate(notes):
        for j in range(step):
            t = j/rate
            amp = 0.30*(1-j/step*0.5)
            s.append(math.sin(2*math.pi*freq*t)*amp*32767)
    _write_wav(path, s)

# ═══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE
# ═══════════════════════════════════════════════════════════════════════════════

def generate_all():
    os.makedirs(LOGOS_DIR, exist_ok=True)
    os.makedirs(DIFF_DIR,  exist_ok=True)
    os.makedirs(SOUNDS_DIR,exist_ok=True)

    # Logos
    for i, entry in enumerate(ALL_LOGOS):
        p = os.path.join(LOGOS_DIR, entry["image"])
        if not os.path.exists(p):
            make_logo(i, entry["name"]).save(p)

    # Images différence (3 variantes)
    for variant, (lname, rname) in enumerate([
        ("diff_mtn_left.png",    "diff_mtn_right.png"),
        ("diff_city_left.png",   "diff_city_right.png"),
        ("diff_forest_left.png", "diff_forest_right.png"),
    ]):
        lp = os.path.join(DIFF_DIR, lname)
        rp = os.path.join(DIFF_DIR, rname)
        if not os.path.exists(lp):
            _make_scene(variant, False).save(lp)
        if not os.path.exists(rp):
            _make_scene(variant, True).save(rp)

    # Audio
    for fname, fn in [
        ("calm.wav",    _make_calm),
        ("tension.wav", _make_tension),
        ("victory.wav", _make_victory),
    ]:
        p = os.path.join(SOUNDS_DIR, fname)
        if not os.path.exists(p):
            fn(p)

if __name__ == "__main__":
    generate_all()
    print("✓ Assets générés.")
