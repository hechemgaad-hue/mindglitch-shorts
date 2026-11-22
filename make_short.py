#!/usr/bin/env python3
"""Générateur de Shorts v2 (1080x1920, 30 fps) optimisé rétention.

- sous-titres mot par mot avec "pop", mot actif en jaune, mots-clés en couleur
- fond animé (dégradé qui dérive, bokeh, vignette), zoom lent + punch-in à chaque phrase
- bande son : voix + musique d'ambiance synthétisée + whoosh à chaque transition
- l'image 1 montre déjà l'accroche (pas de noir), barre de progression discrète

Usage: python3 make_short.py script.json out.mp4
JSON: {"title","hook","facts":[...],"outro" (optionnel),"palette":0-4,"voice":"am_michael"}
Dans le texte, entourer un mot de *astérisques* pour le mettre en couleur (ex: *25%*).
"""
import json, os, re, subprocess, sys, tempfile
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from kokoro_onnx import Kokoro

W, H, FPS = 1080, 1920, 30
MODELS = os.path.expanduser("~/models") if os.path.isdir(os.path.expanduser("~/models")) else "/home/claude/models"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PALETTES = [  # (haut, bas, accent)
    ((18, 8, 50), (130, 40, 170), (255, 214, 64)),
    ((4, 24, 48), (0, 130, 150), (255, 120, 90)),
    ((45, 8, 20), (200, 60, 60), (255, 230, 120)),
    ((8, 36, 28), (60, 170, 100), (255, 240, 130)),
    ((12, 12, 34), (80, 100, 220), (120, 255, 220)),
]
SR = 24000


def ease_out_back(t):
    t = min(max(t, 0), 1)
    c1 = 1.9
    return 1 + (c1 + 1) * (t - 1) ** 3 + c1 * (t - 1) ** 2


# ---------- audio ----------
def whoosh(n_sec=0.45):
    n = int(SR * n_sec)
    noise = np.random.randn(n)
    k = np.linspace(4, 60, n)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):  # filtre passe-bas dont la coupure monte
        acc += (noise[i] - acc) / k[::-1][i]
        out[i] = acc
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out / (np.abs(out).max() + 1e-9) * env * 0.5


def boom(n_sec=0.6):
    t = np.arange(int(SR * n_sec)) / SR
    f = 90 * np.exp(-t * 4) + 35
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6) * 0.9


def music(dur, seed):
    rng = np.random.default_rng(seed)
    t = np.arange(int(SR * dur)) / SR
    roots = [57, 53, 48, 55]  # Am F C G (MIDI)
    chords = [[0, 3, 7], [0, 4, 7], [0, 4, 7], [0, 4, 7]]
    beat = 60 / (78 + rng.integers(0, 12))
    bar = beat * 4
    out = np.zeros_like(t)
    for i, ti in enumerate(t[:: int(SR * 0.01)] if False else []):
        pass
    for b in range(int(dur / bar) + 1):
        r = roots[b % 4]
        s, e = int(b * bar * SR), min(len(t), int((b + 1) * bar * SR))
        if s >= len(t):
            break
        tt = t[s:e] - t[s]
        env = np.minimum(tt / 0.6, 1) * np.minimum((bar - tt) / 0.6, 1)
        for iv in chords[b % 4]:
            fr = 440 * 2 ** ((r + iv - 69) / 12)
            out[s:e] += (np.sin(2 * np.pi * fr * tt) + 0.4 * np.sin(2 * np.pi * 2 * fr * tt)) * env * 0.05
        # arpège pentatonique léger
        scale = [0, 3, 5, 7, 10, 12]
        for q in range(8):
            ts = q * beat / 2
            if ts >= tt[-1] - 0.3:
                break
            note = r + 12 + scale[rng.integers(0, len(scale))]
            fr = 440 * 2 ** ((note - 69) / 12)
            m = (tt >= ts) & (tt < ts + 0.5)
            lt = tt[m] - ts
            out[s:e][m] += np.sin(2 * np.pi * fr * lt) * np.exp(-lt * 7) * 0.035
        # pouls grave sur les temps
        for q in range(4):
            ts = q * beat
            m = (tt >= ts) & (tt < ts + 0.25)
            lt = tt[m] - ts
            out[s:e][m] += np.sin(2 * np.pi * (55 + 40 * np.exp(-lt * 25)) * lt) * np.exp(-lt * 9) * 0.10
    fade = np.minimum(t / 1.0, 1) * np.minimum((dur - t) / 1.2, 1)
    return out * fade


# ---------- texte ----------
def parse_words(sentence):
    words = []
    for tok in sentence.split():
        hl = "*" in tok
        clean = tok.replace("*", "")
        words.append((clean, hl))
    return words


def word_weights(words):
    ws = []
    for w, _ in words:
        x = len(re.sub(r"\W", "", w)) + 2.0
        if w.endswith((".", "!", "?")):
            x += 5
        elif w.endswith((",", ":", ";")):
            x += 3
        ws.append(x)
    return np.array(ws)


FUNC = {"a","an","the","of","or","and","to","in","on","at","for","with","by","from","as","than","that","but","is","are","was","were","your","their","its","his","her","our","my","into","over","if","so","not","no"}


def _chunk(idxs, words, per=3):
    """Découpe optimale (programmation dynamique) : pages de 1 à per mots, pénalise
    les fins sur mot-outil, les pages d'un mot et les tailles déséquilibrées."""
    n = len(idxs)
    if n <= per:
        return [list(idxs)]
    def cost(sz, a, bnd):
        c = 0.0
        last = words[idxs[a + sz - 1]][0].lower().strip(".,!?:;\"'")
        if last in FUNC and a + sz < n:
            c += 9
        if sz == 1:
            c += 7
        c += abs(sz - 2.5) * 0.6
        return c
    best = [(1e9, None)] * (n + 1)
    best[0] = (0.0, None)
    for e in range(1, n + 1):
        for sz in range(1, per + 1):
            a = e - sz
            if a < 0:
                continue
            c = best[a][0] + cost(sz, a, e)
            if c < best[e][0]:
                best[e] = (c, sz)
    out, e = [], n
    while e > 0:
        sz = best[e][1]
        out.append(list(idxs[e - sz:e]))
        e -= sz
    return out[::-1]


def pages(words, per=3):
    """Pages par unités de sens : coupe après ponctuation, puis équilibre."""
    segs, cur = [], []
    for i, (w, hl) in enumerate(words):
        cur.append(i)
        if w.endswith((".", "!", "?", ",", ":", ";")):
            segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    out = []
    for sg in segs:
        out.extend(_chunk(sg, words, per))
    return out


def gradient_half(c1, c2, accent, t, w=540, h=960):
    y = np.linspace(0, 1, h)[:, None]
    shift = 0.5 + 0.5 * np.sin(t * 0.5)
    k = np.clip(y * (0.8 + 0.4 * shift) + 0.08 * np.sin(y * 6 + t), 0, 1)[:, :, None]
    base = np.array(c1) * (1 - k) + np.array(c2) * k
    x = np.linspace(-1, 1, w)[None, :, None]
    glow = np.exp(-((x - 0.5 * np.sin(t * 0.4)) ** 2) * 2.2) * 0.18
    base = base + glow * np.array(accent) * 0.35
    xx = np.linspace(-1, 1, w)[None, :]
    yy = np.linspace(-1, 1, h)[:, None]
    vig = 1 - 0.35 * np.clip(xx ** 2 * 0.6 + yy ** 2 * 0.5, 0, 1)
    return (base * vig[:, :, None]).clip(0, 255).astype("uint8")


def bokeh_sprite(r, color):
    im = Image.new("RGBA", (r * 4, r * 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((r, r, 3 * r, 3 * r), fill=color + (70,))
    return im.filter(ImageFilter.GaussianBlur(r * 0.35))


def layout(words, idxs, font, maxw):
    """Retourne lignes (liste d'indices) pour un groupe de mots."""
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines, cur, cw = [], [], 0
    sp = d.textlength(" ", font=font)
    for i in idxs:
        wl = d.textlength(words[i][0].upper(), font=font)
        if cur and cw + sp + wl > maxw:
            lines.append(cur)
            cur, cw = [], 0
        cur.append(i)
        cw += wl + (sp if len(cur) > 1 else 0)
    if cur:
        lines.append(cur)
    return lines


# ---------- visuels ----------
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EMOJI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "emoji")
_ecache = {}
_gcache = {}
DEFAULT_EMOJIS = ["🧠", "💡", "🤯", "👀", "⚡", "🔥"]


def emoji_img(ch):
    if ch in _ecache:
        return _ecache[ch]
    key = "-".join(f"{ord(c):x}" for c in ch if ord(c) != 0xFE0F)
    path = os.path.join(EMOJI_DIR, key + ".png")
    im = None
    if os.path.exists(path):
        im = Image.open(path).convert("RGBA")
    elif os.path.exists(EMOJI_FONT):
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (160, 140), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 5), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        os.makedirs(EMOJI_DIR, exist_ok=True)
        im.save(path)
    if im is None:
        im = emoji_img("✨") if ch != "✨" else Image.new("RGBA", (10, 10))
    _ecache[ch] = im
    return im


def glow_sprite(color, size=760):
    key = (color, size)
    if key not in _gcache:
        g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((size * 0.18, size * 0.18, size * 0.82, size * 0.82), fill=tuple(color) + (110,))
        _gcache[key] = g.filter(ImageFilter.GaussianBlur(size * 0.12))
    return _gcache[key]


def paste_c(im, spr, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    if scale <= 0.02:
        return
    w, h = spr.size
    sp = spr.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.LANCZOS)
    if angle:
        sp = sp.rotate(angle, expand=True, resample=Image.BICUBIC)
    if alpha < 1:
        a = sp.getchannel("A").point(lambda v: int(v * alpha))
        sp.putalpha(a)
    im.paste(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2)), sp)


def clamp01(x):
    return min(max(x, 0.0), 1.0)


def draw_visual(im, spec, lp, t, accent, fonts):
    d = ImageDraw.Draw(im, "RGBA")
    typ = spec.get("type", "emoji")
    CY = 780  # recentré (avant 640) : le tiers inférieur n'est plus vide
    paste_c(im, glow_sprite(tuple(accent)), W / 2, CY, 1.0 + 0.04 * np.sin(t * 2), alpha=clamp01(lp / 0.3))
    if typ == "emoji":
        ems = spec.get("emojis") or ["✨"]
        n = len(ems)
        size = {1: 400, 2: 310, 3: 260}.get(n, 200)
        xs = {1: [W / 2], 2: [W / 2 - 230, W / 2 + 230], 3: [W / 2 - 300, W / 2, W / 2 + 300]}.get(
            n, [W / 2 - 330 + 220 * i for i in range(n)])
        for i, e in enumerate(ems):
            spr = emoji_img(e)
            base = size / max(spr.size)
            pop = 0.6 + 0.4 * ease_out_back(clamp01((lp - 0.05 * i) / 0.25))  # démarre à 60 % (plus de point minuscule)
            cy = CY + 18 * np.sin(t * 2.6 + i * 1.7) + (0 if n < 3 or i != 1 else -40)
            paste_c(im, spr, xs[i], cy, base * pop, angle=6 * np.sin(t * 2.0 + i))
    elif typ == "bars":
        items = spec["items"]
        unit = spec.get("unit", "")
        mx = max(v for _, v in items)
        n = len(items)
        bw, gap = 250, 110
        total_w = n * bw + (n - 1) * gap
        x0 = W / 2 - total_w / 2
        base_y = CY + 290
        f_val = fonts.setdefault("bv", ImageFont.truetype(FONT, 92))
        f_lab = fonts.setdefault("bl", ImageFont.truetype(FONT, 50))
        for i, (lab, v) in enumerate(items):
            prog = clamp01((lp - 0.12 - 0.22 * i) / 0.7)
            e = 1 - (1 - prog) ** 3
            hgt = 520 * v / mx * e
            x = x0 + i * (bw + gap)
            col = accent + (255,) if i == n - 1 else (255, 255, 255, 190)
            d.rounded_rectangle((x, base_y - hgt, x + bw, base_y), 28, fill=col)
            d.text((x + bw / 2, base_y - hgt - 62), f"{int(round(v * e))}{unit}", font=f_val, fill=(255, 255, 255),
                   anchor="mm", stroke_width=6, stroke_fill=(10, 10, 20))
            d.text((x + bw / 2, base_y + 56), lab.upper(), font=f_lab, fill=(255, 255, 255), anchor="mm",
                   stroke_width=4, stroke_fill=(10, 10, 20))
    elif typ == "grid":
        total, on = spec.get("total", 20), spec.get("on", 5)
        cols = 5
        rows = -(-total // cols)
        cell, step = 110, 160
        gx = W / 2 - (cols - 1) * step / 2
        gy = CY - 60 - (rows - 1) * step / 2
        for i in range(total):
            r, c = divmod(i, cols)
            pop = ease_out_back(clamp01((lp - 0.03 * i) / 0.3))
            is_on = i < on
            rad = cell / 2 * max(pop, 0)
            cx, cy = gx + c * step, gy + r * step
            col = accent + (255,) if is_on else (255, 255, 255, 80)
            d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=col)
        if spec.get("label"):
            f_lab = fonts.setdefault("gl", ImageFont.truetype(FONT, 54))
            d.text((W / 2, gy + (rows - 1) * step + 120), spec["label"].upper(), font=f_lab, fill=(255, 255, 255),
                   anchor="mm", stroke_width=5, stroke_fill=(10, 10, 20))
    elif typ == "number":
        v = spec["value"]
        e = 1 - (1 - clamp01(lp / 0.9)) ** 3
        txt = f"{int(round(v * e))}{spec.get('unit', '')}"
        full = f"{int(round(v))}{spec.get('unit', '')}"
        # taille auto : le nombre final doit tenir en largeur (marge 90 px)
        nsz = 330
        while nsz > 120 and ImageDraw.Draw(im).textlength(full, font=fonts.setdefault(("nn", nsz), ImageFont.truetype(FONT, nsz))) + 30 > W - 180:
            nsz -= 10
        f_n = fonts.setdefault(("nn", nsz), ImageFont.truetype(FONT, nsz))
        pop = 1 + 0.08 * (1 - clamp01(lp / 0.4))
        d.text((W / 2, CY), txt, font=f_n, fill=accent, anchor="mm", stroke_width=10, stroke_fill=(10, 10, 20))
        if spec.get("label"):
            f_lab = fonts.setdefault("nl", ImageFont.truetype(FONT, 58))
            d.text((W / 2, CY + 230), spec["label"].upper(), font=f_lab, fill=(255, 255, 255), anchor="mm",
                   stroke_width=5, stroke_fill=(10, 10, 20))
    # flash de transition
    if lp < 0.12:
        a = int(90 * (1 - lp / 0.12))
        ImageDraw.Draw(im, "RGBA").rectangle((0, 0, W, H), fill=(255, 255, 255, a))


def pick_size(words, page):
    for size in (150, 134, 118, 104, 92, 80, 70, 60):
        f = _gcache.setdefault(("font", size), ImageFont.truetype(FONT, size))
        lines = layout(words, page, f, W - 190)
        d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        sp = d.textlength(" ", font=f)
        ok = len(lines) <= 2
        for ln in lines:
            ws = [d.textlength(words[i][0].upper(), font=f) for i in ln]
            if sum(ws) + sp * (len(ws) - 1) + 0.14 * max(ws) > W - 130:
                ok = False
        if ok:
            return size
    return 60


def main(script_path, out):
    s = json.load(open(script_path))
    sentences = [s["hook"]] + s["facts"] + ([s["outro"]] if s.get("outro") else [])
    pal = PALETTES[s.get("palette", 0) % len(PALETTES)]
    c1, c2, accent = pal
    kok = Kokoro(f"{MODELS}/kokoro.onnx", f"{MODELS}/voices.bin")
    voice = s.get("voice", "am_michael")
    visuals = s.get("visuals", [])
    vis_fonts = {}

    # --- voix & timing ---
    segs, t0 = [], 0.0
    audio_parts = []
    for si, sent in enumerate(sentences):
        plain = sent.replace("*", "")
        a, sr = kok.create(plain, voice=voice, speed=1.1, lang="en-us")
        assert sr == SR
        gap = 0.18 if si < len(sentences) - 1 else 0.55
        a = np.concatenate([a, np.zeros(int(SR * gap), dtype=a.dtype)])
        words = parse_words(sent)
        dur = len(a) / SR
        spoken = dur - gap
        wts = word_weights(words)
        edges = np.concatenate([[0], np.cumsum(wts) / wts.sum()]) * spoken
        segs.append(dict(start=t0, dur=dur, words=words, edges=edges + t0, pages=pages(words)))
        audio_parts.append(a)
        t0 += dur
    total = t0
    voice_track = np.concatenate(audio_parts)

    # --- mix audio ---
    seed = abs(hash(s["hook"])) % (2 ** 32)
    mix = np.zeros(len(voice_track))
    mus = music(total, seed)
    mus = np.pad(mus, (0, max(0, len(mix) - len(mus))))
    mix += mus[: len(mix)] * 1.0
    sfx = np.zeros_like(mix)
    wsh = whoosh()
    for i, sg in enumerate(segs):
        st = int(max(sg["start"] - 0.08, 0) * SR)
        w_ = wsh[: len(sfx) - st]
        sfx[st: st + len(w_)] += w_ * 0.45
    b = boom()
    sfx[: len(b)] += b[: len(sfx)] * 0.5
    peak = np.abs(voice_track).max() + 1e-9
    # ducking : la musique baisse (~-9 dB) quand la voix parle, enveloppe lissée
    vt = voice_track / peak
    hop = int(SR * 0.02)
    nb = len(vt) // hop + 1
    rms = np.array([np.sqrt(np.mean(vt[i * hop:(i + 1) * hop] ** 2)) if i * hop < len(vt) else 0.0 for i in range(nb)])
    act = (rms > 0.02).astype(float)
    k = np.hanning(21); k /= k.sum()
    act = np.convolve(np.pad(act, 10, mode="edge"), k, mode="valid")[:nb]
    gain = 1.0 - 0.65 * act
    gain_s = np.interp(np.arange(len(mix)) / hop, np.arange(nb), gain)
    mix = mix * gain_s
    mixed = vt * 0.85 + mix + sfx
    mixed = mixed / max(1.0, np.abs(mixed).max() / 0.95)
    tmp = tempfile.mkdtemp()
    raw = f"{tmp}/raw.wav"
    wav = f"{tmp}/mix.wav"
    sf.write(raw, mixed.astype("float32"), SR)
    # normalisation du volume : loudnorm 2 passes, cible -14 LUFS, crête -1.5 dBTP
    tgt = "I=-14:TP=-1.5:LRA=11"
    try:
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", raw, "-af", f"loudnorm={tgt}:print_format=json", "-f", "null", "-"],
                           capture_output=True, text=True)
        m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
        af = (f"loudnorm={tgt}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
              f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", af, "-ar", str(SR), wav], check=True)
    except Exception as e:
        print("loudnorm ignoré :", e)
        wav = raw

    # --- vidéo ---
    rng = np.random.default_rng(seed)
    sprites = []
    for _ in range(14):
        r = int(rng.integers(14, 46))
        col = [accent, (255, 255, 255), c2][int(rng.integers(0, 3))]
        sprites.append(dict(img=bokeh_sprite(r, tuple(int(v) for v in col)),
                            x=rng.uniform(0, 540), y=rng.uniform(0, 960), vx=rng.uniform(-8, 8), vy=-rng.uniform(10, 40)))
    f_title = ImageFont.truetype(FONT, 40)
    nframes = int(total * FPS) + 1
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    fonts = {}
    for fi in range(nframes):
        t = fi / FPS
        # phrase courante
        si = next((i for i, sg in enumerate(segs) if t < sg["start"] + sg["dur"]), len(segs) - 1)
        sg = segs[si]
        local = t - sg["start"]
        bgh = Image.fromarray(gradient_half(c1, c2, accent, t))
        for sp in sprites:
            x = (sp["x"] + sp["vx"] * t) % 560 - 10
            y = (sp["y"] + sp["vy"] * t) % 980 - 10
            bgh.paste(sp["img"], (int(x - sp["img"].width / 2), int(y - sp["img"].height / 2)), sp["img"])
        # zoom lent + punch-in au début de phrase
        zoom = 1.0 + 0.05 * (local / max(sg["dur"], 0.1)) + 0.05 * (1 - ease_out_back(min(local / 0.25, 1))) * -1
        zoom = max(1.0, 1.0 + 0.045 * (local / max(sg["dur"], 0.1)) + 0.06 * max(0, 1 - local / 0.22))
        cw, ch = 540 / zoom, 960 / zoom
        bgh = bgh.crop((int((540 - cw) / 2), int((960 - ch) / 2), int((540 + cw) / 2), int((960 + ch) / 2)))
        im = bgh.resize((W, H), Image.BILINEAR)
        d = ImageDraw.Draw(im, "RGBA")
        # barre de progression
        d.rounded_rectangle((80, 135, W - 80, 143), 4, fill=(255, 255, 255, 60))
        d.rounded_rectangle((80, 135, 80 + int((W - 160) * t / total), 143), 4, fill=accent + (255,))
        d.text((W // 2, 100), "MINDGLITCH", font=f_title, fill=(255, 255, 255, 190), anchor="mm")
        spec = visuals[si] if si < len(visuals) and visuals[si] else {"type": "emoji", "emojis": [DEFAULT_EMOJIS[si % len(DEFAULT_EMOJIS)]]}
        draw_visual(im, spec, local, t, accent, vis_fonts)
        d = ImageDraw.Draw(im, "RGBA")
        # page de sous-titres courante
        words, edges = sg["words"], sg["edges"]
        cur_w = max(0, int(np.searchsorted(edges, t, side="right") - 1))
        cur_w = min(cur_w, len(words) - 1)
        page = next(p for p in sg["pages"] if cur_w in p) if any(cur_w in p for p in sg["pages"]) else sg["pages"][-1]
        size = pick_size(words, page)
        font = fonts.setdefault(size, ImageFont.truetype(FONT, size))
        lines = layout(words, page, font, W - 190)
        lh = size * 1.22
        y0 = H * 0.725 - lh * len(lines) / 2 + lh / 2
        pop_t = (t - edges[cur_w]) / 0.16
        for li, ln in enumerate(lines):
            widths = [d.textlength(words[i][0].upper(), font=font) * (1.12 if i == cur_w else 1.0) for i in ln]
            sp_w = d.textlength(" ", font=font) * 1.15
            tw = sum(widths) + sp_w * (len(ln) - 1)
            x = W / 2 - tw / 2
            for i, wd in zip(ln, widths):
                txt = words[i][0].upper()
                cx, cy = x + wd / 2, y0 + li * lh
                active = i == cur_w
                hl = words[i][1]
                col = accent if (active or hl) else (255, 255, 255)
                if i > cur_w:
                    col = (255, 255, 255)
                fnt = font
                if active:
                    sc = 1.0 + 0.12 * ease_out_back(pop_t) if pop_t < 1 else 1.12
                    fnt = fonts.setdefault(int(size * sc), ImageFont.truetype(FONT, int(size * sc)))
                d.text((cx + 6, cy + 8), txt, font=fnt, fill=(0, 0, 0, 200), anchor="mm")
                d.text((cx, cy), txt, font=fnt, fill=col, anchor="mm", stroke_width=6, stroke_fill=(10, 10, 20))
                x += wd + sp_w
        ff.stdin.write(im.tobytes())
    ff.stdin.close()
    ff.wait()
    print("OK", out, f"{total:.1f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
