"""
utils/asset_generator.py
Génère les logos (60) et les sons (3 WAV).
Les images de différences sont fournies manuellement (1.Left.jpg … 30.Right.jpg).
"""
import os, math, wave, struct
from PIL import Image, ImageDraw

from config import LOGOS_DIR, SOUNDS_DIR
from games.logo_data import ALL_LOGOS

# ═══════════════════════════════════════════════════════════════════════════════
# LOGOS — 60 logos stylisés générés par PIL
# ═══════════════════════════════════════════════════════════════════════════════

LOGO_THEMES = [
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
    _draw_shape(draw, 150, 85, 52, shape, (255,255,255,50))
    _draw_shape(draw, 150, 85, 38, shape,
                (255,255,255) if shape != "circle" else tuple(min(c+30,255) for c in c1))
    initials = name[:2] if len(name)>=2 else name[0]
    _text_centered(draw, initials, 90, 28, tuple(c1), 300)
    _text_centered(draw, name, 165, 18, (255,255,255), 300)
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
    os.makedirs(LOGOS_DIR,  exist_ok=True)
    os.makedirs(SOUNDS_DIR, exist_ok=True)

    # ── Logos (60) ────────────────────────────────────────────────
    for i, entry in enumerate(ALL_LOGOS):
        p = os.path.join(LOGOS_DIR, entry["image"])
        if not os.path.exists(p):
            make_logo(i, entry["name"]).save(p)

    # ── Audio ─────────────────────────────────────────────────────
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
    print("✓ 60 logos + 3 sons générés.")